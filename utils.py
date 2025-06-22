# Utility functions for the application
import numpy as np
import logging

logger = logging.getLogger(__name__)

def format_results_for_display(results):
    """
    Format algorithm results for display.
    
    Args:
        results: Dictionary of algorithm results
        
    Returns:
        dict: Formatted results
    """
    generations = list(range(len(results['best_fitness_history'])))
    
    return {
        'generations': generations,
        'best_fitness': results['best_fitness_history'],
        'avg_fitness': results['avg_fitness_history'],
        'final_best_fitness': results['best_fitness']
    }

def get_line_styles():
    """
    Get line styles for different charts.
    
    Returns:
        dict: Different line styles
    """
    return {
        'best': 'dashed',
        'avg': 'solid',
        'improved': 'solid',
        'standard': 'dashed',
        'param1': 'solid',
        'param2': 'dashed',
        'param3': 'dotted',
        'param4': 'dashdot'
    }

def analyze_taguchi_results(results):
    """
    Analyze Taguchi experiment results.
    
    Args:
        results: List of experiment results
        
    Returns:
        dict: Analysis of parameter effects
    """
    # Extract parameter values and results
    experiments = []
    for result in results:
        experiments.append({
            'overbest': result['overbest'],
            'ps': result['ps'],
            'pcross': result['pcross'],
            'fitness': result['final_fitness']
        })
    
    # Calculate average effects at each level
    overbest_levels = sorted(list(set(exp['overbest'] for exp in experiments)))
    ps_levels = sorted(list(set(exp['ps'] for exp in experiments)))
    pcross_levels = sorted(list(set(exp['pcross'] for exp in experiments)))
    
    overbest_effects = {level: [] for level in overbest_levels}
    ps_effects = {level: [] for level in ps_levels}
    pcross_effects = {level: [] for level in pcross_levels}
    
    for exp in experiments:
        overbest_effects[exp['overbest']].append(exp['fitness'])
        ps_effects[exp['ps']].append(exp['fitness'])
        pcross_effects[exp['pcross']].append(exp['fitness'])
    
    # Calculate averages
    overbest_avgs = {level: np.mean(values) for level, values in overbest_effects.items()}
    ps_avgs = {level: np.mean(values) for level, values in ps_effects.items()}
    pcross_avgs = {level: np.mean(values) for level, values in pcross_effects.items()}
    
    # Find optimal levels
    optimal_overbest = max(overbest_avgs.items(), key=lambda x: x[1])[0]
    optimal_ps = max(ps_avgs.items(), key=lambda x: x[1])[0]
    optimal_pcross = max(pcross_avgs.items(), key=lambda x: x[1])[0]
    
    return {
        'overbest_effects': overbest_avgs,
        'ps_effects': ps_avgs,
        'pcross_effects': pcross_avgs,
        'optimal': {
            'overbest': optimal_overbest,
            'ps': optimal_ps,
            'pcross': optimal_pcross
        }
    }
