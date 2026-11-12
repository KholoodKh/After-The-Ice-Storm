# Greyhaven Emergency Radio Deployment Optimization

Optimization of emergency radio station deployment in Greyhaven following a severe ice storm. The project investigates single-objective and multi-objective optimization approaches to determine effective locations and configurations for four portable radio stations under different emergency operating situations.

## 1. Project Overview

The objective is to optimize the deployment of four portable radio stations to provide reliable emergency communication coverage across Greyhaven.

Each station is described by six decision variables:

| Variable | Description |
|---|---|
| `x` | Easting coordinate |
| `y` | Northing coordinate |
| `p` | Transmission power |
| `h` | Antenna height |
| `c` | Communication channel |
| `z` | Station activation status |

The complete deployment contains 24 decision variables.

The optimization considers three operating situations:

- **Initial Response:** Normal emergency response conditions.
- **Evening Pressure:** Increased communication demand from shelters and clinics.
- **Northern Outage:** Increased demand and modified communication conditions in the northern region.

## 2. Optimization Assignments

### Assignment A – Location Optimization

Optimizes station locations and transmission power while keeping the other station settings fixed:

- Antenna height: `h = 4`
- Communication channel: `c = 1`
- Activation status: `z = 1`

The purpose is to investigate how station placement and transmission power affect emergency communication performance.

### Assignment B – Full Configuration Optimization

Optimizes all six decision variables for each station:

- Location (`x`, `y`)
- Transmission power (`p`)
- Antenna height (`h`)
- Communication channel (`c`)
- Activation status (`z`)

This assignment provides a more flexible deployment optimization problem.

### Assignment C – Multi-Objective Optimization

Considers three objectives simultaneously:

- `Q`: Communication service quality
- `C`: Deployment cost
- `E`: Energy consumption

The problem minimizes:

\[
\min [Q,C,E]
\]

Since these objectives may conflict, the algorithms generate a set of non-dominated solutions representing different trade-offs.

The resulting Pareto fronts are compared using Hypervolume (HV).

## 3. Optimization Algorithms

### Assignments A and B

Implemented using **MEALPY**.

The tested algorithms include:

- Genetic Algorithm (GA)
- Particle Swarm Optimization (PSO)
- Grey Wolf Optimizer (GWO)
- Improved Grey Wolf Optimizer (IGWO)
- Whale Optimization Algorithm (WOA)
- Harris Hawks Optimization (HHO)

### Assignment C

Implemented using **pymoo**.

The tested multi-objective algorithms include:

- NSGA-II
- NSGA-III
- SPEA2

## 4. Experimental Configuration

The experiments use the following settings:

| Parameter | Value |
|---|---:|
| Independent runs | 31 |
| Population size | 50 |
| Maximum evaluations per run | 10,000 |
| Random seeds | 1–31 |
| Operating situations | 3 |

Each algorithm is evaluated independently using the same evaluation budget and operating situation.

The experiments record:

- Best objective values
- Convergence history
- Execution time
- Final solutions
- Pareto fronts (Assignment C)

## 5. Evaluation and Visualization

The project generates visualizations and summaries to compare optimization algorithms.

**Assignments A and B:**
- Fitness distribution box plots
- Mean convergence curves
- Convergence curves with standard deviation
- Runtime comparisons
- Best fitness comparisons
- Best deployment visualizations

**Assignment C:**
- Pareto front visualizations
- Hypervolume convergence plots
- Hypervolume comparisons
- Best compromise solution tables
- Deployment visualizations

## 6. Technologies and Dependencies

- Python
- MEALPY
- pymoo
- SAES
- NumPy
- Pandas
- SciPy
- scikit-learn
- Matplotlib
- Seaborn
- OpenPyXL
- scikit-posthocs
- statsmodels

## 7. Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

Create and activate a virtual environment (optional):

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 8. Running the Experiments

Run the relevant Python scripts or notebooks for each assignment.

Before running experiments, configure:

- The operating situation.
- The optimization assignment.
- The selected optimization algorithms.
- The population size and evaluation budget.
- The number of independent runs.

For example, the experimental configuration uses:

```python
n_runs = 31
pop_size = 50
max_fe = 10000
```

## 9. Results

Experimental results are stored and analyzed for each algorithm and operating situation.

The results include convergence data, runtime measurements, objective values, and optimized station configurations.

Assignment C additionally stores the final Pareto solutions and their corresponding decision vectors.

## 10. Reproducibility

To support reproducibility:

- Each independent run uses a separate random seed.
- All algorithms use the specified evaluation budget.
- Experimental settings are kept consistent across comparisons.
- Dependencies and their versions are listed in `requirements.txt`.

## 11. Project Structure

The repository contains the problem implementation, optimization experiments, visualization utilities, and experimental results.

A suggested organization is:

```text
Greyhaven-Optimization/
│
├── greyhaven_problem.py
├── greyhaven_moo_problem.py
├── requirements.txt
├── README.md
│
├── assignment_A/
├── assignment_B/
├── assignment_C/
│
├── results/
│   ├── assignment_A/
│   ├── assignment_B/
│   └── assignment_C/
│
└── figures/
```

*The directory names above are illustrative; adjust them to match the actual repository.*

## 12. License

This project was developed for academic research and experimental evaluation of optimization algorithms for emergency radio deployment.
