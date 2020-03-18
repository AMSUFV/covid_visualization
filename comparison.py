import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.style.use('seaborn')

displacement = 0.005

population_size = 100
# patient zero
patient_zero = np.random.randint(0, population_size)

fig, axs = plt.subplots(1, 1)

population = np.zeros(population_size)
population[patient_zero] = 1

locations = np.random.rand(population_size, 2)

# four states: healthy (0), infected (1), cured (2), deceased (3)
states = [x for x in range(4)]
colors = ['#81cc95',  # healthy
          '#ff8282',  # infected
          '#8ceaff',  # cured
          '#000000',  # dead
          ]


def animate(*args):
    global population
    global locations

    axs.clear()
    for state, color in zip(states, colors):
        individuals = np.isin(population, state)
        if individuals.sum() != 0:
            subset = locations[individuals]
            axs.scatter(subset[:, 0], subset[:, 1], c=color)
            axs.set_aspect('equal')
            axs.set_xlim(0, 1)
            axs.set_ylim(0, 1)

    # movement
    movement = (2 * displacement) * np.random.rand(population_size, 2) - displacement
    locations = locations + movement
    locations = np.where(locations > 1, -(locations - 1) + 1, locations)
    locations = abs(locations)


ani = animation.FuncAnimation(fig, animate, interval=25)
plt.show()
