import numpy as np
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ImmuneGeneticAlgorithm(ABC):
    """Abstract base class for immune genetic algorithms."""
    
    def __init__(self, population_size=50, max_generations=50, overbest=8, 
                 ps=0.65, pcross=0.8, pmutation=0.1, use_elite_retention=False):
        """
        Initialize the immune genetic algorithm.
        
        Args:
            population_size (int): Size of the population
            max_generations (int): Maximum number of generations
            overbest (int): Memory capacity (size of memory pool)
            ps (float): Diversity evaluation parameter
            pcross (float): Crossover probability
            pmutation (float): Mutation probability
            use_elite_retention (bool): Whether to use elite retention strategy
        """
        self.population_size = population_size
        self.max_generations = max_generations
        self.overbest = overbest
        self.ps = ps
        self.pcross = pcross
        self.pmutation = pmutation
        self.use_elite_retention = use_elite_retention
        
        # Antigen (risk factor) and antibody (emergency plan) length
        self.antigen_length = 20  # Example value, could be parameterized
        self.antibody_length = 20  # Same as antigen for simplicity
        
        # Generate a random antigen (risk factor)
        self.antigen = np.random.randint(0, 2, self.antigen_length)
        
        # Results tracking
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.generation_history = []
    
    def binary_encode(self, individual):
        """Convert individual to binary representation."""
        # In this implementation, individuals are already binary
        return individual
    
    def calculate_affinity(self, antibody):
        """
        Calculate affinity between antibody and antigen using Hamming distance.
        
        Args:
            antibody: Binary representation of an antibody
            
        Returns:
            float: Affinity value (higher is better)
        """
        # Convert to binary if not already
        binary_antibody = self.binary_encode(antibody)
        binary_antigen = self.antigen
        
        # Calculate Hamming distance
        hamming_distance = np.sum(binary_antibody != binary_antigen)
        
        # Affinity function F(x,y) = 1 / (1 + G(x,y))
        affinity = 1.0 / (1.0 + hamming_distance)
        
        return affinity
    
    def calculate_similarity(self, antibody1, antibody2):
        """
        Calculate similarity between two antibodies.
        
        Args:
            antibody1, antibody2: Binary representations of antibodies
            
        Returns:
            float: Similarity value (higher means more similar)
        """
        # For simplicity, use fraction of matching positions
        matching_positions = np.sum(antibody1 == antibody2)
        similarity = matching_positions / len(antibody1)
        
        return similarity
    
    def calculate_concentration(self, antibody, population, threshold=0.8):
        """
        Calculate concentration of an antibody in the population.
        
        Args:
            antibody: The antibody to calculate concentration for
            population: List of all antibodies in the population
            threshold: Similarity threshold to count as similar
            
        Returns:
            float: Concentration value
        """
        similar_count = 0
        for other in population:
            if np.array_equal(antibody, other):
                continue  # Skip identical antibody
                
            similarity = self.calculate_similarity(antibody, other)
            if similarity > threshold:
                similar_count += 1
                
        concentration = similar_count / len(population)
        return concentration
    
    def calculate_expected_reproduction(self, antibody, affinities, concentrations):
        """
        Calculate expected reproduction rate for an antibody.
        
        Args:
            antibody: The antibody to calculate for
            affinities: List of all affinities in the population
            concentrations: List of all concentrations in the population
            
        Returns:
            float: Expected reproduction rate
        """
        idx = next((i for i, a in enumerate(self.population) if np.array_equal(a, antibody)), None)
        if idx is None:
            return 0
            
        affinity = affinities[idx]
        concentration = concentrations[idx]
        
        # E_k = ps * (F_k / sum_F) + (1-ps) * (C_k / sum_C)
        total_affinity = sum(affinities)
        total_concentration = sum(concentrations) if sum(concentrations) > 0 else 1
        
        expected_rate = self.ps * (affinity / total_affinity)
        expected_rate += (1 - self.ps) * (concentration / total_concentration)
        
        return expected_rate
    
    def selection(self, expected_rates):
        """
        Select parents for reproduction using roulette wheel selection.
        
        Args:
            expected_rates: List of expected reproduction rates
            
        Returns:
            list: Selected indices
        """
        # Normalize rates if necessary
        if sum(expected_rates) == 0:
            probs = [1/len(expected_rates) for _ in expected_rates]
        else:
            probs = [rate/sum(expected_rates) for rate in expected_rates]
            
        # Select population_size individuals
        selected_indices = np.random.choice(
            len(expected_rates), 
            size=self.population_size - self.overbest,  # Subtract memory size
            p=probs,
            replace=True
        )
        
        return selected_indices
    
    def crossover(self, parent1, parent2):
        """
        Perform single-point crossover between two parents.
        
        Args:
            parent1, parent2: Parent individuals
            
        Returns:
            tuple: Two offspring
        """
        if np.random.random() > self.pcross:
            return parent1.copy(), parent2.copy()
            
        # Single point crossover
        crossover_point = np.random.randint(1, len(parent1) - 1)
        
        child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
        child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))
        
        return child1, child2
    
    def mutation(self, individual):
        """
        Perform mutation on an individual.
        
        Args:
            individual: The individual to mutate
            
        Returns:
            array: Mutated individual
        """
        mutated = individual.copy()
        
        for i in range(len(mutated)):
            if np.random.random() < self.pmutation:
                # Flip bit (binary mutation)
                mutated[i] = 1 - mutated[i]
                
        return mutated
    
    def initialize_population(self):
        """
        Initialize random population of antibodies.
        
        Returns:
            array: Initial population
        """
        return np.random.randint(0, 2, (self.population_size, self.antibody_length))
    
    @abstractmethod
    def update_memory(self, population, affinities):
        """
        Update memory with high-affinity antibodies.
        Must be implemented by subclasses.
        """
        pass
    
    def run(self):
        """
        Run the immune genetic algorithm.
        
        Returns:
            dict: Results including best and average fitness history
        """
        # Initialize population
        self.population = self.initialize_population()
        
        # Initialize memory pool
        self.memory_pool = np.zeros((self.overbest, self.antibody_length), dtype=int)
        
        # Track best solution
        best_individual = None
        best_fitness = 0
        
        # Early convergence tracking
        stagnation_counter = 0
        convergence_threshold = 0.99  # Stop if fitness reaches 99% of theoretical maximum
        
        # For each generation
        for generation in range(self.max_generations):
            logger.info(f"Generation {generation+1}/{self.max_generations}")
            
            # Calculate affinities
            affinities = [self.calculate_affinity(antibody) for antibody in self.population]
            
            # Find best individual
            current_best_idx = np.argmax(affinities)
            current_best_fitness = affinities[current_best_idx]
            current_best_individual = self.population[current_best_idx].copy()
            
            # Update best overall
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_individual = current_best_individual.copy()
                stagnation_counter = 0
            else:
                stagnation_counter += 1
                
            # Early convergence check
            if best_fitness >= convergence_threshold:
                logger.info(f"Early convergence at generation {generation+1}")
                # Fill remaining history with current values
                for g in range(generation + 1, self.max_generations):
                    self.best_fitness_history.append(best_fitness)
                    self.avg_fitness_history.append(np.mean(affinities))
                    self.generation_history.append(g)
                break
                
            # Stagnation check (no improvement for 10 generations)
            if stagnation_counter >= 10:
                logger.info(f"Stagnation detected at generation {generation+1}, stopping early")
                break
                
            # Calculate average fitness
            average_fitness = np.mean(affinities)
            
            # Store history
            self.best_fitness_history.append(current_best_fitness)
            self.avg_fitness_history.append(average_fitness)
            self.generation_history.append(generation)
            
            # Log progress
            logger.info(f"Best fitness: {current_best_fitness:.4f}, Avg fitness: {average_fitness:.4f}")
            
            # Calculate concentrations
            concentrations = [self.calculate_concentration(antibody, self.population) 
                             for antibody in self.population]
            
            # Calculate expected reproduction rates
            expected_rates = [self.calculate_expected_reproduction(antibody, affinities, concentrations) 
                             for antibody in self.population]
            
            # Update memory (implementation differs between standard and improved versions)
            self.memory_pool = self.update_memory(self.population, affinities)
            
            # Selection
            selected_indices = self.selection(expected_rates)
            
            # Create new population
            new_population = np.zeros((self.population_size - self.overbest, self.antibody_length), dtype=int)
            
            # Crossover and mutation
            for i in range(0, len(selected_indices), 2):
                if i + 1 < len(selected_indices):
                    parent1 = self.population[selected_indices[i]]
                    parent2 = self.population[selected_indices[i+1]]
                    
                    # Crossover
                    child1, child2 = self.crossover(parent1, parent2)
                    
                    # Mutation
                    child1 = self.mutation(child1)
                    child2 = self.mutation(child2)
                    
                    # Add to new population
                    idx = i // 2 * 2
                    if idx < len(new_population):
                        new_population[idx] = child1
                    if idx + 1 < len(new_population):
                        new_population[idx + 1] = child2
            
            # Combine memory pool and new population
            self.population = np.vstack((self.memory_pool, new_population))
        
        # Return results
        return {
            'best_individual': best_individual.tolist() if best_individual is not None else None,
            'best_fitness': best_fitness,
            'best_fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'generations': self.generation_history
        }

class StandardImmuneGeneticAlgorithm(ImmuneGeneticAlgorithm):
    """Standard immune genetic algorithm implementation."""
    
    def __init__(self, population_size=50, max_generations=50, overbest=8, 
                 ps=0.65, pcross=0.8, pmutation=0.1, use_elite_retention=False):
        """Initialize with elite retention always off for Standard Algorithm."""
        # Force elite retention to be False for standard algorithm
        super().__init__(population_size, max_generations, overbest, ps, pcross, pmutation, False)
    
    def update_memory(self, population, affinities):
        """
        Update memory in standard IGA (without elite retention strategy).
        
        Args:
            population: Current population
            affinities: Corresponding affinities
            
        Returns:
            array: Updated memory pool
        """
        # Get indices of top individuals by affinity
        top_indices = np.argsort(affinities)[-self.overbest:]
        
        # Extract top individuals
        memory = np.array([population[i] for i in top_indices])
        
        return memory

class ImprovedImmuneGeneticAlgorithm(ImmuneGeneticAlgorithm):
    """Improved immune genetic algorithm with elite retention strategy."""
    
    def __init__(self, population_size=50, max_generations=50, overbest=8, 
                 ps=0.65, pcross=0.8, pmutation=0.1, use_elite_retention=True):
        """Initialize with elite retention enabled by default for Improved Algorithm."""
        super().__init__(population_size, max_generations, overbest, ps, pcross, pmutation, use_elite_retention)
    
    def update_memory(self, population, affinities):
        """
        Update memory with elite retention strategy.
        
        Args:
            population: Current population
            affinities: Corresponding affinities
            
        Returns:
            array: Updated memory pool
        """
        if self.use_elite_retention:
            # Number of elite individuals to preserve
            num_elite = min(3, self.overbest)  # Default to 3 or smaller if overbest is smaller
            
            # Get indices of top individuals by affinity
            sorted_indices = np.argsort(affinities)
            elite_indices = sorted_indices[-num_elite:]
            remaining_indices = sorted_indices[-(self.overbest):-num_elite] if num_elite < self.overbest else []
            
            # Extract elite individuals
            elite_memory = np.array([population[i] for i in elite_indices])
            
            # Extract remaining memory individuals
            remaining_memory = np.array([population[i] for i in remaining_indices])
            
            # Combine elite and remaining memory
            if len(remaining_indices) > 0:
                memory = np.vstack((elite_memory, remaining_memory))
            else:
                memory = elite_memory
                
            return memory
        else:
            # If elite retention is disabled, use standard memory update
            top_indices = np.argsort(affinities)[-self.overbest:]
            memory = np.array([population[i] for i in top_indices])
            return memory


class TournamentSelectionIGA(ImmuneGeneticAlgorithm):
    """Immune genetic algorithm with tournament selection strategy."""
    
    def __init__(self, population_size=50, max_generations=50, overbest=8, 
                 ps=0.65, pcross=0.8, pmutation=0.1, use_elite_retention=True,
                 tournament_size=3):
        """
        Initialize with tournament selection.
        
        Args:
            tournament_size: Number of individuals in each tournament
        """
        super().__init__(population_size, max_generations, overbest, ps, pcross, pmutation, use_elite_retention)
        self.tournament_size = min(tournament_size, population_size)
    
    def selection(self, expected_rates):
        """
        Select parents using tournament selection.
        
        Args:
            expected_rates: List of expected reproduction rates
            
        Returns:
            list: Selected indices
        """
        selected_indices = []
        
        # Need to select enough parents for the new population
        for _ in range(self.population_size - self.overbest):
            # Select tournament participants randomly
            tournament_indices = np.random.choice(len(expected_rates), 
                                                 size=self.tournament_size, 
                                                 replace=False)
            
            # Find the winner (highest expected rate)
            tournament_rates = [expected_rates[i] for i in tournament_indices]
            winner_idx = tournament_indices[np.argmax(tournament_rates)]
            
            selected_indices.append(winner_idx)
        
        return np.array(selected_indices)
    
    def update_memory(self, population, affinities):
        """
        Update memory in tournament selection IGA.
        
        Args:
            population: Current population
            affinities: Corresponding affinities
            
        Returns:
            array: Updated memory pool
        """
        if self.use_elite_retention:
            # Number of elite individuals to preserve
            num_elite = min(3, self.overbest)  # Default to 3 or smaller if overbest is smaller
            
            # Get indices of top individuals by affinity
            sorted_indices = np.argsort(affinities)
            elite_indices = sorted_indices[-num_elite:]
            remaining_indices = sorted_indices[-(self.overbest):-num_elite] if num_elite < self.overbest else []
            
            # Extract elite individuals
            elite_memory = np.array([population[i] for i in elite_indices])
            
            # Extract remaining memory individuals
            remaining_memory = np.array([population[i] for i in remaining_indices])
            
            # Combine elite and remaining memory
            if len(remaining_indices) > 0:
                memory = np.vstack((elite_memory, remaining_memory))
            else:
                memory = elite_memory
                
            return memory
        else:
            # If elite retention is disabled, use standard memory update
            top_indices = np.argsort(affinities)[-self.overbest:]
            memory = np.array([population[i] for i in top_indices])
            return memory


class AdaptiveMutationIGA(ImprovedImmuneGeneticAlgorithm):
    """Immune genetic algorithm with adaptive mutation rate."""
    
    def __init__(self, population_size=50, max_generations=50, overbest=8, 
                 ps=0.65, pcross=0.8, pmutation=0.1, use_elite_retention=True,
                 min_mutation=0.01, max_mutation=0.25):
        """
        Initialize with adaptive mutation rate.
        
        Args:
            min_mutation: Minimum mutation rate
            max_mutation: Maximum mutation rate
        """
        super().__init__(population_size, max_generations, overbest, ps, pcross, pmutation, use_elite_retention)
        self.min_mutation = min_mutation
        self.max_mutation = max_mutation
        self.current_mutation = pmutation
    
    def mutation(self, individual):
        """
        Perform mutation with adaptive rate.
        
        Args:
            individual: The individual to mutate
            
        Returns:
            array: Mutated individual
        """
        # Create a copy of the individual
        mutated = np.copy(individual)
        
        # Perform mutation with current rate
        for i in range(len(mutated)):
            if np.random.random() < self.current_mutation:
                mutated[i] = 1 - mutated[i]  # Flip bit
        
        return mutated
    
    def run(self):
        """
        Run algorithm with adaptive mutation rate.
        
        Returns:
            dict: Results including best and average fitness history
        """
        # Initialize population
        self.population = self.initialize_population()
        
        # Initialize memory pool
        self.memory_pool = None
        
        # Initialize best solution tracking
        best_fitness = 0
        best_individual = None
        
        # Initialize history
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.generation_history = []
        
        # Evolutionary process
        for generation in range(1, self.max_generations + 1):
            logger.info(f"Generation {generation}/{self.max_generations}")
            
            # Calculate affinity of each antibody
            affinities = [self.calculate_affinity(antibody) for antibody in self.population]
            
            # Track best solution
            max_affinity_idx = np.argmax(affinities)
            max_affinity = affinities[max_affinity_idx]
            
            if max_affinity > best_fitness:
                best_fitness = max_affinity
                best_individual = self.population[max_affinity_idx]
            
            # Calculate current average fitness
            avg_fitness = np.mean(affinities)
            
            # Adjust mutation rate based on population diversity
            diversity = 1.0 - (avg_fitness / (best_fitness + 1e-10))  # Avoid division by zero
            self.current_mutation = self.min_mutation + diversity * (self.max_mutation - self.min_mutation)
            
            # Store history
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            self.generation_history.append(generation)
            
            logger.info(f"Best fitness: {best_fitness:.4f}, Avg fitness: {avg_fitness:.4f}")
            
            # Check for early convergence
            if best_fitness >= 1.0:  # Assuming 1.0 is the maximum possible fitness
                logger.info(f"Converged at generation {generation}")
                # Fill remaining history with the same values
                for g in range(generation + 1, self.max_generations + 1):
                    self.best_fitness_history.append(best_fitness)
                    self.avg_fitness_history.append(avg_fitness)
                    self.generation_history.append(g)
                break
            
            # Calculate similarity and concentration
            concentrations = [self.calculate_concentration(antibody, self.population) 
                             for antibody in self.population]
            
            # Calculate expected reproduction rates
            expected_rates = [self.calculate_expected_reproduction(antibody, affinities, concentrations) 
                             for antibody in self.population]
            
            # Update memory (implementation differs between standard and improved versions)
            self.memory_pool = self.update_memory(self.population, affinities)
            
            # Selection
            selected_indices = self.selection(expected_rates)
            
            # Create new population
            new_population = np.zeros((self.population_size - self.overbest, self.antibody_length), dtype=int)
            
            # Crossover and mutation
            for i in range(0, len(selected_indices), 2):
                if i + 1 < len(selected_indices):
                    parent1 = self.population[selected_indices[i]]
                    parent2 = self.population[selected_indices[i+1]]
                    
                    # Crossover
                    child1, child2 = self.crossover(parent1, parent2)
                    
                    # Mutation with adaptive rate
                    child1 = self.mutation(child1)
                    child2 = self.mutation(child2)
                    
                    # Add to new population
                    idx = i // 2 * 2
                    if idx < len(new_population):
                        new_population[idx] = child1
                    if idx + 1 < len(new_population):
                        new_population[idx + 1] = child2
            
            # Combine memory pool and new population
            self.population = np.vstack((self.memory_pool, new_population))
        
        # Return results
        return {
            'best_individual': best_individual.tolist() if best_individual is not None else None,
            'best_fitness': best_fitness,
            'best_fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'generations': self.generation_history,
            'final_mutation_rate': self.current_mutation
        }


class OptimizedImmuneGeneticAlgorithm(ImprovedImmuneGeneticAlgorithm):
    """高度优化的免疫遗传算法，集成多种效率提升策略"""
    
    def __init__(self, population_size=50, max_generations=50, overbest=8, 
                 ps=0.65, pcross=0.8, pmutation=0.1, use_elite_retention=True,
                 early_stop_threshold=0.99, stagnation_limit=8):
        super().__init__(population_size, max_generations, overbest, ps, pcross, pmutation, use_elite_retention)
        self.early_stop_threshold = early_stop_threshold
        self.stagnation_limit = stagnation_limit
        self.adaptive_mutation = True
        self.min_mutation = 0.005
        self.max_mutation = 0.2
        self.current_mutation = pmutation
    
    def calculate_affinity_vectorized(self, population):
        """向量化的亲和度计算，提高计算效率"""
        # 使用numpy广播进行批量计算
        population_array = np.array(population)
        antigen_array = np.tile(self.antigen, (len(population), 1))
        
        # 批量计算汉明距离
        hamming_distances = np.sum(population_array != antigen_array, axis=1)
        
        # 批量计算亲和度
        affinities = 1.0 / (1.0 + hamming_distances)
        
        return affinities.tolist()
    
    def adaptive_mutation_rate(self, best_fitness, avg_fitness, generation):
        """自适应变异率调整"""
        # 基于多样性的自适应调整
        diversity = 1.0 - (avg_fitness / (best_fitness + 1e-10))
        
        # 基于代数的衰减
        generation_factor = max(0.1, 1.0 - generation / self.max_generations)
        
        # 综合调整
        self.current_mutation = self.min_mutation + diversity * generation_factor * (self.max_mutation - self.min_mutation)
        
        return self.current_mutation
    
    def run(self):
        """优化的运行流程"""
        # 初始化
        self.population = self.initialize_population()
        self.memory_pool = None
        
        best_fitness = 0
        best_individual = None
        stagnation_counter = 0
        
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.generation_history = []
        
        for generation in range(self.max_generations):
            # 使用向量化计算提高效率
            affinities = self.calculate_affinity_vectorized(self.population)
            
            # 更新最佳解
            max_affinity_idx = np.argmax(affinities)
            max_affinity = affinities[max_affinity_idx]
            
            if max_affinity > best_fitness:
                best_fitness = max_affinity
                best_individual = self.population[max_affinity_idx].copy()
                stagnation_counter = 0
            else:
                stagnation_counter += 1
            
            avg_fitness = np.mean(affinities)
            
            # 早期停止检查
            if best_fitness >= self.early_stop_threshold:
                logger.info(f"Early convergence at generation {generation+1}")
                # 填充剩余历史记录
                for g in range(generation, self.max_generations):
                    self.best_fitness_history.append(best_fitness)
                    self.avg_fitness_history.append(avg_fitness)
                    self.generation_history.append(g)
                break
            
            # 停滞检查
            if stagnation_counter >= self.stagnation_limit:
                logger.info(f"Stagnation detected at generation {generation+1}")
                # 增加种群多样性
                num_random = max(2, self.population_size // 10)
                random_indices = np.random.choice(self.population_size, num_random, replace=False)
                for idx in random_indices:
                    self.population[idx] = np.random.randint(0, 2, self.antibody_length)
                stagnation_counter = 0
            
            # 自适应变异率
            if self.adaptive_mutation:
                self.adaptive_mutation_rate(best_fitness, avg_fitness, generation)
            
            # 记录历史
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            self.generation_history.append(generation)
            
            logger.info(f"Generation {generation+1}: Best={best_fitness:.4f}, Avg={avg_fitness:.4f}, Mutation={self.current_mutation:.4f}")
            
            # 计算浓度（优化版本）
            concentrations = self._calculate_concentrations_optimized(affinities)
            
            # 计算期望繁殖率
            expected_rates = [self.calculate_expected_reproduction(antibody, affinities, concentrations) 
                             for antibody in self.population]
            
            # 更新记忆池
            self.memory_pool = self.update_memory(self.population, affinities)
            
            # 选择
            selected_indices = self.selection(expected_rates)
            
            # 生成新种群
            new_population = self._create_new_population_optimized(selected_indices)
            
            # 合并记忆池和新种群
            self.population = np.vstack((self.memory_pool, new_population))
        
        return {
            'best_individual': best_individual.tolist() if best_individual is not None else None,
            'best_fitness': best_fitness,
            'best_fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'generations': self.generation_history,
            'final_mutation_rate': self.current_mutation
        }
    
    def _calculate_concentrations_optimized(self, affinities):
        """优化的浓度计算"""
        # 简化浓度计算，基于亲和度分布
        sorted_affinities = np.sort(affinities)
        concentrations = []
        
        for affinity in affinities:
            # 基于亲和度排名计算浓度
            rank = np.searchsorted(sorted_affinities, affinity)
            concentration = rank / len(affinities)
            concentrations.append(concentration)
        
        return concentrations
    
    def _create_new_population_optimized(self, selected_indices):
        """优化的新种群生成"""
        new_population = np.zeros((self.population_size - self.overbest, self.antibody_length), dtype=int)
        
        # 批量交叉和变异
        for i in range(0, len(selected_indices), 2):
            if i + 1 < len(selected_indices):
                parent1 = self.population[selected_indices[i]]
                parent2 = self.population[selected_indices[i+1]]
                
                # 交叉
                child1, child2 = self.crossover(parent1, parent2)
                
                # 使用当前自适应变异率
                child1 = self._mutation_optimized(child1)
                child2 = self._mutation_optimized(child2)
                
                # 添加到新种群
                idx = i // 2 * 2
                if idx < len(new_population):
                    new_population[idx] = child1
                if idx + 1 < len(new_population):
                    new_population[idx + 1] = child2
        
        return new_population
    
    def _mutation_optimized(self, individual):
        """优化的变异操作"""
        mutated = individual.copy()
        
        # 使用当前自适应变异率
        mutation_mask = np.random.random(len(mutated)) < self.current_mutation
        mutated[mutation_mask] = 1 - mutated[mutation_mask]
        
        return mutated


class DiversityEnhancedIGA(ImprovedImmuneGeneticAlgorithm):
    """Immune genetic algorithm with enhanced diversity preservation."""
    
    def __init__(self, population_size=50, max_generations=50, overbest=8, 
                 ps=0.65, pcross=0.8, pmutation=0.1, use_elite_retention=True,
                 diversity_threshold=0.8):
        """
        Initialize with diversity enhancement.
        
        Args:
            diversity_threshold: Threshold for triggering diversity enhancement
        """
        super().__init__(population_size, max_generations, overbest, ps, pcross, pmutation, use_elite_retention)
        self.diversity_threshold = diversity_threshold
    
    def calculate_population_diversity(self, population):
        """
        Calculate diversity of the population.
        
        Args:
            population: The population to analyze
            
        Returns:
            float: Diversity measure (higher means more diverse)
        """
        n = len(population)
        diversity_sum = 0
        
        # Sample pairs of individuals to estimate diversity
        sample_size = min(n * (n - 1) // 2, 100)  # Limit computation for large populations
        pairs = np.random.choice(n, size=(sample_size, 2), replace=True)
        
        for i, j in pairs:
            if i != j:
                similarity = self.calculate_similarity(population[i], population[j])
                diversity_sum += (1 - similarity)
        
        return diversity_sum / sample_size if sample_size > 0 else 0
    
    def enhance_diversity(self, population, num_to_replace):
        """
        Enhance diversity by replacing similar individuals.
        
        Args:
            population: Current population
            num_to_replace: Number of individuals to replace
            
        Returns:
            array: Population with enhanced diversity
        """
        n = len(population)
        similarity_matrix = np.zeros((n, n))
        
        # Calculate similarity between all pairs
        for i in range(n):
            for j in range(i+1, n):
                similarity = self.calculate_similarity(population[i], population[j])
                similarity_matrix[i, j] = similarity
                similarity_matrix[j, i] = similarity
        
        # Calculate total similarity for each individual
        similarity_sums = np.sum(similarity_matrix, axis=1)
        
        # Get indices of individuals with highest similarity to others
        most_similar_indices = np.argsort(similarity_sums)[-num_to_replace:]
        
        # Create enhanced population
        enhanced_population = np.copy(population)
        
        # Replace most similar individuals with new random ones
        for idx in most_similar_indices:
            enhanced_population[idx] = np.random.randint(0, 2, self.antibody_length)
        
        return enhanced_population
    
    def run(self):
        """
        Run algorithm with diversity enhancement.
        
        Returns:
            dict: Results including best and average fitness history
        """
        # Initialize population
        self.population = self.initialize_population()
        
        # Initialize memory pool
        self.memory_pool = None
        
        # Initialize best solution tracking
        best_fitness = 0
        best_individual = None
        
        # Initialize history
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.generation_history = []
        self.diversity_history = []
        
        # Stagnation counter
        stagnation_counter = 0
        last_best_fitness = 0
        
        # Evolutionary process
        for generation in range(1, self.max_generations + 1):
            logger.info(f"Generation {generation}/{self.max_generations}")
            
            # Calculate affinity of each antibody
            affinities = [self.calculate_affinity(antibody) for antibody in self.population]
            
            # Track best solution
            max_affinity_idx = np.argmax(affinities)
            max_affinity = affinities[max_affinity_idx]
            
            if max_affinity > best_fitness:
                best_fitness = max_affinity
                best_individual = self.population[max_affinity_idx]
                stagnation_counter = 0
            else:
                stagnation_counter += 1
            
            # Check for stagnation
            if stagnation_counter >= 5:  # If no improvement for 5 generations
                # Calculate population diversity
                current_diversity = self.calculate_population_diversity(self.population)
                
                # If diversity is below threshold, enhance it
                if current_diversity < self.diversity_threshold:
                    num_to_replace = max(2, self.population_size // 10)  # Replace 10% of population
                    self.population = self.enhance_diversity(self.population, num_to_replace)
                    logger.info(f"Diversity enhanced at generation {generation}")
                
                stagnation_counter = 0  # Reset counter
            
            # Calculate current average fitness
            avg_fitness = np.mean(affinities)
            
            # Store history
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            self.generation_history.append(generation)
            
            logger.info(f"Best fitness: {best_fitness:.4f}, Avg fitness: {avg_fitness:.4f}")
            
            # Check for early convergence
            if best_fitness >= 1.0:  # Assuming 1.0 is the maximum possible fitness
                logger.info(f"Converged at generation {generation}")
                # Fill remaining history with the same values
                for g in range(generation + 1, self.max_generations + 1):
                    self.best_fitness_history.append(best_fitness)
                    self.avg_fitness_history.append(avg_fitness)
                    self.generation_history.append(g)
                break
            
            # Calculate similarity and concentration
            concentrations = [self.calculate_concentration(antibody, self.population) 
                             for antibody in self.population]
            
            # Calculate expected reproduction rates
            expected_rates = [self.calculate_expected_reproduction(antibody, affinities, concentrations) 
                             for antibody in self.population]
            
            # Update memory (implementation differs between standard and improved versions)
            self.memory_pool = self.update_memory(self.population, affinities)
            
            # Selection
            selected_indices = self.selection(expected_rates)
            
            # Create new population
            new_population = np.zeros((self.population_size - self.overbest, self.antibody_length), dtype=int)
            
            # Crossover and mutation
            for i in range(0, len(selected_indices), 2):
                if i + 1 < len(selected_indices):
                    parent1 = self.population[selected_indices[i]]
                    parent2 = self.population[selected_indices[i+1]]
                    
                    # Crossover
                    child1, child2 = self.crossover(parent1, parent2)
                    
                    # Mutation
                    child1 = self.mutation(child1)
                    child2 = self.mutation(child2)
                    
                    # Add to new population
                    idx = i // 2 * 2
                    if idx < len(new_population):
                        new_population[idx] = child1
                    if idx + 1 < len(new_population):
                        new_population[idx + 1] = child2
            
            # Combine memory pool and new population
            self.population = np.vstack((self.memory_pool, new_population))
            
            # Update last best fitness
            last_best_fitness = best_fitness
        
        # Return results
        return {
            'best_individual': best_individual.tolist() if best_individual is not None else None,
            'best_fitness': best_fitness,
            'best_fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'generations': self.generation_history
        }
