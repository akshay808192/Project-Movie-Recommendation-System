"""
Hybrid Recommendation Orchestrator & Cold-Start Strategy Router
Automatically switches between Popularity Cold-Start, Adaptive Hybrid Transition,
and Pure Collaborative Filtering based on user interaction maturity.
"""

from typing import List, Dict, Set, Optional, Tuple
from backend.app.recommender.cold_start import ColdStartRecommender
from backend.app.recommender.collaborative import CollaborativeFilteringRecommender

class HybridRecommender:
    def __init__(
        self,
        cold_start_recommender: ColdStartRecommender,
        collaborative_recommender: CollaborativeFilteringRecommender,
        movie_metadata: Dict[int, dict]
    ):
        self.cold_start = cold_start_recommender
        self.collaborative = collaborative_recommender
        self.movie_metadata = movie_metadata

    def recommend(
        self,
        user_ratings: List[Tuple[int, float]],
        user_favorites: Optional[List[int]] = None,
        user_history: Optional[List[int]] = None,
        genre: Optional[str] = None,
        top_n: int = 20
    ) -> Dict:
        """
        Automatically select strategy and compute recommendations.
        Returns dictionary with:
        - strategy
        - strategy_badge
        - strategy_description
        - user_interaction_count
        - recommendations: list of items
        """
        exclude_mids = set()
        for mid, _ in user_ratings:
            exclude_mids.add(mid)
        if user_favorites:
            for mid in user_favorites:
                exclude_mids.add(mid)
        if user_history:
            for mid in user_history:
                exclude_mids.add(mid)

        total_interactions = len(user_ratings) + len(user_favorites or [])

        # --- CASE 1: NEW USER (0 interactions) -> COLD START POPULARITY ---
        if total_interactions == 0:
            recs = self.cold_start.recommend(
                exclude_mids=exclude_mids,
                genre=genre,
                top_n=top_n
            )
            return {
                'strategy': 'COLD_START_POPULARITY',
                'strategy_badge': 'Cold-Start Popularity',
                'strategy_description': (
                    'Welcome! Because you have no rating history yet, our cold-start system '
                    'recommends the highest-rated and critically acclaimed films with verified reviews.'
                ),
                'user_interaction_count': 0,
                'recommendations': recs
            }

        # --- CASE 2: MATURE USER (>= 5 interactions) -> PURE COLLABORATIVE FILTERING ---
        if total_interactions >= 5:
            cf_recs = self.collaborative.recommend(
                user_ratings=user_ratings,
                user_favorites=user_favorites,
                exclude_mids=exclude_mids,
                genre=genre,
                top_n=top_n
            )
            # If CF returned enough items, return CF
            if len(cf_recs) >= min(10, top_n):
                return {
                    'strategy': 'COLLABORATIVE_FILTERING',
                    'strategy_badge': 'Personalized Collaborative Filtering',
                    'strategy_description': (
                        f'Personalized specifically for your taste! Recommendations generated '
                        f'using Item-to-Item Collaborative Filtering from your {total_interactions} ratings & favorites.'
                    ),
                    'user_interaction_count': total_interactions,
                    'recommendations': cf_recs
                }

        # --- CASE 3: SPARSE USER (1 to 4 interactions) -> HYBRID BLENDING ---
        # User has a few ratings, but not enough for full CF diversity alone
        alpha = total_interactions / 5.0 # Ranges from 0.2 to 0.8
        
        # Get collaborative candidates
        cf_recs = self.collaborative.recommend(
            user_ratings=user_ratings,
            user_favorites=user_favorites,
            exclude_mids=exclude_mids,
            genre=genre,
            top_n=top_n * 2
        )

        # Get popularity candidates
        pop_recs = self.cold_start.recommend(
            exclude_mids=exclude_mids,
            genre=genre,
            top_n=top_n * 2
        )

        # Normalize CF scores to 0..1
        max_cf = max([r['cf_score'] for r in cf_recs], default=1.0)
        if max_cf <= 0:
            max_cf = 1.0

        cf_dict = {}
        for r in cf_recs:
            cf_dict[r['movieId']] = {
                'norm_score': r['cf_score'] / max_cf,
                'item': r
            }

        # Max pop score ~ 4.4
        pop_dict = {}
        for r in pop_recs:
            norm_pop = r['popularity_score'] / 4.4
            pop_dict[r['movieId']] = {
                'norm_score': norm_pop,
                'item': r
            }

        all_candidate_ids = list(set(list(cf_dict.keys()) + list(pop_dict.keys())))
        blended_ranked = []

        for mid in all_candidate_ids:
            cf_part = cf_dict.get(mid, {}).get('norm_score', 0.0)
            pop_part = pop_dict.get(mid, {}).get('norm_score', 0.0)

            # Blended score
            blend_score = (alpha * cf_part) + ((1.0 - alpha) * pop_part)

            # Determine base item representation
            if mid in cf_dict:
                item_data = cf_dict[mid]['item']
                source = item_data.get('source_movie_title')
                expl = (
                    f"Hybrid Pick: {int(alpha*100)}% based on your rating of '{source}' + "
                    f"{int((1-alpha)*100)}% community popularity"
                )
            else:
                item_data = pop_dict[mid]['item']
                expl = f"Hybrid Pick: Critically popular film matching your emerging preferences"

            match_pct = min(98, max(78, int(80 + (blend_score * 18))))

            blended_item = {
                **item_data,
                'cf_score': round(float(blend_score), 3),
                'match_percentage': match_pct,
                'explanation': expl
            }
            blended_ranked.append(blended_item)

        blended_ranked.sort(key=lambda x: x['cf_score'], reverse=True)
        final_recs = blended_ranked[:top_n]

        return {
            'strategy': 'HYBRID_TRANSITION',
            'strategy_badge': f'Adaptive Hybrid ({int(alpha*100)}% CF / {int((1-alpha)*100)}% Pop)',
            'strategy_description': (
                f'Emerging profile ({total_interactions}/5 ratings): Combining collaborative signals '
                f'from your recent ratings with community popularity.'
            ),
            'user_interaction_count': total_interactions,
            'recommendations': final_recs
        }
