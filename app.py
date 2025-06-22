import os
import logging
from flask import Flask, render_template, request, jsonify
from algorithm import (ImprovedImmuneGeneticAlgorithm, StandardImmuneGeneticAlgorithm, 
                     TournamentSelectionIGA, AdaptiveMutationIGA, DiversityEnhancedIGA)
import numpy as np

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "immune_genetic_algorithm_secret")

@app.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')

@app.route('/run_algorithm', methods=['POST'])
def run_algorithm():
    """Run the immune genetic algorithm with the provided parameters."""
    try:
        data = request.json

        # Extract parameters
        population_size = int(data.get('population_size', 50))
        max_generations = int(data.get('max_generations', 50))
        overbest = int(data.get('overbest', 8))
        ps = float(data.get('ps', 0.65))
        pcross = float(data.get('pcross', 0.8))
        pmutation = float(data.get('pmutation', 0.1))
        algorithm_type = data.get('algorithm_type', 'improved')
        use_elite_retention = data.get('use_elite_retention', True)

        # Initialize appropriate algorithm
        if algorithm_type == 'improved':
            algorithm = ImprovedImmuneGeneticAlgorithm(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention
            )
        elif algorithm_type == 'standard':
            algorithm = StandardImmuneGeneticAlgorithm(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=False  # Always false for standard algorithm
            )
        elif algorithm_type == 'tournament':
            tournament_size = int(data.get('tournament_size', 3))
            algorithm = TournamentSelectionIGA(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention,
                tournament_size=tournament_size
            )
        elif algorithm_type == 'adaptive_mutation':
            min_mutation = float(data.get('min_mutation', 0.01))
            max_mutation = float(data.get('max_mutation', 0.25))
            algorithm = AdaptiveMutationIGA(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention,
                min_mutation=min_mutation,
                max_mutation=max_mutation
            )
        elif algorithm_type == 'diversity_enhanced':
            diversity_threshold = float(data.get('diversity_threshold', 0.8))
            algorithm = DiversityEnhancedIGA(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention,
                diversity_threshold=diversity_threshold
            )
        else:  # Default to standard if unknown type
            algorithm = StandardImmuneGeneticAlgorithm(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=False
            )

        # Run algorithm
        result = algorithm.run()

        return jsonify({
            'success': True,
            'result': result,
            'message': f"Algorithm completed successfully with final fitness: {result['best_fitness_history'][-1]:.4f}"
        })
    except Exception as e:
        logger.exception("Error running algorithm")
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        }), 500

@app.route('/taguchi_experiment', methods=['POST'])
def run_taguchi_experiment():
    """Run Taguchi experiment to find optimal parameters."""
    try:
        data = request.json
        max_generations = int(data.get('max_generations', 50))

        # Get Taguchi experiment levels from the request or use defaults
        overbest_levels = data.get('overbest_levels', [4, 8, 12])
        ps_levels = data.get('ps_levels', [0.35, 0.65, 0.95])
        pcross_levels = data.get('pcross_levels', [0.6, 0.8, 1.0])

        # L9 orthogonal array design
        L9 = [
            [0, 0, 0], [0, 1, 1], [0, 2, 2],
            [1, 0, 1], [1, 1, 2], [1, 2, 0],
            [2, 0, 2], [2, 1, 0], [2, 2, 1]
        ]

        results = []

        for i, experiment in enumerate(L9):
            # Extract parameters for this experiment
            param_overbest = overbest_levels[experiment[0]]
            param_ps = ps_levels[experiment[1]]
            param_pcross = pcross_levels[experiment[2]]

            # Run algorithm with these parameters
            algorithm = ImprovedImmuneGeneticAlgorithm(
                population_size=50,
                max_generations=max_generations,
                overbest=param_overbest,
                ps=param_ps,
                pcross=param_pcross,
                pmutation=0.1
            )

            experiment_result = algorithm.run()

            # Store results
            results.append({
                'experiment': i + 1,
                'overbest': param_overbest,
                'ps': param_ps,
                'pcross': param_pcross,
                'final_fitness': experiment_result['best_fitness_history'][-1],
                'data': experiment_result
            })

        # Calculate optimal parameter combination
        avg_overbest = [0, 0, 0]
        avg_ps = [0, 0, 0]
        avg_pcross = [0, 0, 0]

        for i, experiment in enumerate(L9):
            avg_overbest[experiment[0]] += results[i]['final_fitness']
            avg_ps[experiment[1]] += results[i]['final_fitness']
            avg_pcross[experiment[2]] += results[i]['final_fitness']

        avg_overbest = [x/3 for x in avg_overbest]
        avg_ps = [x/3 for x in avg_ps]
        avg_pcross = [x/3 for x in avg_pcross]

        optimal_overbest = overbest_levels[np.argmax(avg_overbest)]
        optimal_ps = ps_levels[np.argmax(avg_ps)]
        optimal_pcross = pcross_levels[np.argmax(avg_pcross)]

        return jsonify({
            'success': True,
            'experiments': results,
            'optimal_parameters': {
                'overbest': optimal_overbest,
                'ps': optimal_ps,
                'pcross': optimal_pcross
            },
            'parameter_response': {
                'overbest': [{'level': level, 'value': avg} for level, avg in zip(overbest_levels, avg_overbest)],
                'ps': [{'level': level, 'value': avg} for level, avg in zip(ps_levels, avg_ps)],
                'pcross': [{'level': level, 'value': avg} for level, avg in zip(pcross_levels, avg_pcross)]
            }
        })
    except Exception as e:
        logger.exception("Error running Taguchi experiment")
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        }), 500

@app.route('/compare_algorithms', methods=['POST'])
def compare_algorithms():
    """Compare any two immune genetic algorithm variants."""
    try:
        data = request.json

        # Extract common parameters
        population_size = int(data.get('population_size', 50))
        max_generations = int(data.get('max_generations', 50))
        overbest = int(data.get('overbest', 8))
        ps = float(data.get('ps', 0.65))
        pcross = float(data.get('pcross', 0.8))
        pmutation = float(data.get('pmutation', 0.1))

        # Get parameters for first algorithm
        first_algorithm = data.get('first_algorithm', {})
        first_type = first_algorithm.get('algorithm_type', 'improved')
        use_elite_retention_first = first_algorithm.get('use_elite_retention', True)

        # Get parameters for second algorithm
        second_algorithm = data.get('second_algorithm', {})
        second_type = second_algorithm.get('algorithm_type', 'standard')
        use_elite_retention_second = second_algorithm.get('use_elite_retention', False)

        # Initialize first algorithm based on type
        if first_type == 'improved':
            first_alg = ImprovedImmuneGeneticAlgorithm(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention_first
            )
        elif first_type == 'standard':
            first_alg = StandardImmuneGeneticAlgorithm(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=False  # Always false for standard
            )
        elif first_type == 'tournament':
            tournament_size = int(first_algorithm.get('tournament_size', 3))
            first_alg = TournamentSelectionIGA(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention_first,
                tournament_size=tournament_size
            )
        elif first_type == 'adaptive_mutation':
            min_mutation = float(first_algorithm.get('min_mutation', 0.01))
            max_mutation = float(first_algorithm.get('max_mutation', 0.25))
            first_alg = AdaptiveMutationIGA(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention_first,
                min_mutation=min_mutation,
                max_mutation=max_mutation
            )
        elif first_type == 'diversity_enhanced':
            diversity_threshold = float(first_algorithm.get('diversity_threshold', 0.8))
            first_alg = DiversityEnhancedIGA(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention_first,
                diversity_threshold=diversity_threshold
            )
        else:
            # Default to improved if type is unknown
            first_alg = ImprovedImmuneGeneticAlgorithm(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention_first
            )

        # Initialize second algorithm based on type
        if second_type == 'improved':
            second_alg = ImprovedImmuneGeneticAlgorithm(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention_second
            )
        elif second_type == 'standard':
            second_alg = StandardImmuneGeneticAlgorithm(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=False  # Always false for standard
            )
        elif second_type == 'tournament':
            tournament_size = int(second_algorithm.get('tournament_size', 3))
            second_alg = TournamentSelectionIGA(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention_second,
                tournament_size=tournament_size
            )
        elif second_type == 'adaptive_mutation':
            min_mutation = float(second_algorithm.get('min_mutation', 0.01))
            max_mutation = float(second_algorithm.get('max_mutation', 0.25))
            second_alg = AdaptiveMutationIGA(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention_second,
                min_mutation=min_mutation,
                max_mutation=max_mutation
            )
        elif second_type == 'diversity_enhanced':
            diversity_threshold = float(second_algorithm.get('diversity_threshold', 0.8))
            second_alg = DiversityEnhancedIGA(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=use_elite_retention_second,
                diversity_threshold=diversity_threshold
            )
        else:
            # Default to standard if type is unknown
            second_alg = StandardImmuneGeneticAlgorithm(
                population_size=population_size,
                max_generations=max_generations,
                overbest=overbest,
                ps=ps,
                pcross=pcross,
                pmutation=pmutation,
                use_elite_retention=False
            )

        # Run both algorithms
        first_result = first_alg.run()
        second_result = second_alg.run()

        # Add algorithm type to results
        first_result['algorithm_type'] = first_type
        second_result['algorithm_type'] = second_type

        return jsonify({
            'success': True,
            'first': first_result,
            'second': second_result
        })
    except Exception as e:
        logger.exception("Error comparing algorithms")
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)