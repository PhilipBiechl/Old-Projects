import pygame
import sys
import math
import numpy as np
import typer
import logging

TAILING_LEN = 150
REBOUND_FACTOR = 0.7
MAX_BODYS = 10
BODY_MASS = 10
INIT_BODY_COUNT = 3
BODY_COLORS = [
    (217, 237, 146),
    (93, 115, 126),
    (30, 96, 145),
    (62, 63, 63),
    (143, 45, 86),
    (116, 0, 184),
    (56, 4, 14),
]

class Body:
    def __init__(
        self, x, y, z, mass, velocity, color, rebound_factor, screen_width, screen_height
    ):
        self.x = x
        self.y = y
        self.z = z
        self.mass = mass
        self.radius = int(math.sqrt(mass) * 2)
        self.vx, self.vy, self.vz = velocity
        self.color = color
        self.trace = []
        self.rebound_factor = rebound_factor
        self.screen_width = screen_width
        self.screen_height = screen_height

    def __eq__(self, other) -> bool:
        if self.color == other.color:
            return True
        else:
            return False

    def calculate_grav_force(self, bodies: list, g: float):
        force = (0, 0, 0)
        for body in bodies:
            if body != self:
                force += calculate_gravitational_force(self, body, g)
        force1x, force1y = add_tuples(force)
        force1z = 0
        self.update(force1x, force1y, force1z)

    def update(self, force_x: float, force_y: float, force_z: float):
        ax = force_x / self.mass
        ay = force_y / self.mass
        az = force_z / self.mass
        self.vx += ax
        self.vy += ay
        self.vz += az
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.check_boundaries()
        self.update_trace()

    def update_trace(self):
        self.trace.append((self.x, self.y))
        if len(self.trace) >= TAILING_LEN:
            self.trace.pop(0)

    def check_boundaries(self):
        if self.y < 0:
            self.y = 0
            self.vy *= -self.rebound_factor
        elif self.y > self.screen_height:
            self.y = self.screen_height
            self.vy *= -self.rebound_factor
        if self.x < 0:
            self.x = 0
            self.vx *= -self.rebound_factor
        elif self.x > self.screen_width:
            self.x = self.screen_width
            self.vx *= -self.rebound_factor

    def draw(self, screen):
        for point in self.trace:
            pygame.draw.circle(screen, self.color, point, 1)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


def calculate_gravitational_force(p1: Body, p2: Body, g: float) -> tuple:
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dz = p2.z - p1.z
    distance = max(1, math.sqrt(dx**2 + dy**2 + dz**2))
    if distance < 40:
        return (0, 0, 0)
    force = (g * p1.mass * p2.mass) / (distance**2)
    angleXY = math.atan2(dy, dx)
    angleYZ = math.atan2(dz, dy)
    angleZX = math.atan2(dx, dz)
    force_x = force * math.cos(angleXY)
    force_y = force * math.sin(angleXY)
    force_z = force * math.cos(angleZX)
    return (force_x, force_y, force_z)


def add_tuples(tuple: tuple) -> tuple:
    even = 0
    odd = 0
    for i in range(len(tuple)):
        if i % 2 == 0:
            even += tuple[i]
        else:
            odd += tuple[i]
    return (even, odd)


def main(
    width: int = typer.Option(1500, help="Width of the screen"),
    height: int = typer.Option(900, help="Height of the screen"),
    x: int = typer.Option(800, help="X of the simulation"),
    y: int = typer.Option(800, help="Y of the simulation"),
    z: int = typer.Option(800, help="Z of the simulation"),
    angle_phi: int = typer.Option(45, help="Phi angle of the simulation window"),
    angle_theta: int = typer.Option(45, help="Theta angle of the simulation window"),
    max_bodies: int = typer.Option(
        MAX_BODYS, help="Maximum number of bodies to had to the simulation."
    ),
    rebound_factor: float = typer.Option(
        REBOUND_FACTOR,
        help="Factor strength to apply when bodies when bodies bounce off the limits of the screen.",
    ),
    mass: int = typer.Option(BODY_MASS, help="Default mass of the bodies."),
    g: int = typer.Option(9.81, help="The gravitational constant."),
    clock: int = typer.Option(
        60, help="Framerate to delay the game to the given ticks."
    ),
):
    # SETUP
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    # CALCULATE NECESSARY TRIGONOMETRY
    side = 200
    #x = np.sqrt(side**2 - (side / 2) ** 2)
    initial_x = width / 2 - side / 2
    initial_y = 400
    initial_z = 10

    # INITIAL BODIES
    bodies = []
    for i in range(INIT_BODY_COUNT):
        bodies.append(
            Body(
                initial_x,
                initial_y,
                initial_z,
                mass=mass,
                velocity=(0.1, 0.1, -0.1),
                color=(116, 148, 196),
                rebound_factor=rebound_factor,
                screen_height=height,
                screen_width=width,
            )
        )

    ''' body1 = Body(
        initial_x,
        initial_y,
        initial_z,
        mass=mass,
        velocity=(0.1, 0.1, -0.1),
        color=(116, 148, 196),
        rebound_factor=rebound_factor,
        screen_height=height,
        screen_width=width,
    )
    body2 = Body(
        (initial_x + (initial_x + side)) / 2,
        initial_y - x,
        initial_z,
        mass=mass,
        velocity=(-0.1, 0.1, 0.1),
        color=(106, 77, 97),
        rebound_factor=rebound_factor,
        screen_height=height,
        screen_width=width,
    )
    body3 = Body(
        initial_x + side,
        initial_y,
        initial_z,
        mass=mass,
        velocity=(0.1, -0.1, 0.1),
        color=(195, 212, 7),
        rebound_factor=rebound_factor,
        screen_height=height,
        screen_width=width,
    )
    bodies = [body1, body2, body3] '''

    # MAIN LOOP
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    if len(bodies) < max_bodies:
                        mouse = pygame.mouse.get_pos()
                        bodies.append(
                            Body(
                                mouse[0],
                                mouse[1],
                                10,
                                mass=mass,
                                velocity=(0.1, 0.1, 0.1),
                                color=BODY_COLORS[len(bodies) - INIT_BODY_COUNT],
                                rebound_factor=rebound_factor,
                                screen_height=height,
                                screen_width=width,
                            )
                        )
                    else:
                        logging.warning("You've reached the maximum of bodies!")

                elif event.button == 1:
                    (angle_phi, angle_theta) = pygame.mouse.get_pos()
                    #angle_phi = pos[0]
                    #angle_theta = pos[1]
                    logging.info(angle_phi, angle_theta)
                
        screen.fill((0, 0, 0))

        for body in bodies:
            body.calculate_grav_force(bodies, g=g)
            body.draw(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    typer.run(main)
