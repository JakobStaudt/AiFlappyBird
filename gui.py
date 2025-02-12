import pygame
import settings


class GUI:
    def __init__(self):
        pygame.init()

        self.gap_half_height = settings.gap_height / 2
        self.pipe_width = settings.pipe_width

        self.fps = 60
        self.fpsClock = pygame.time.Clock()

        width, height = 720, 480
        self.screen = pygame.display.set_mode((width, height), vsync=True)

        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        self.frame_font = pygame.font.SysFont("Arial", 30)
        self.debug_font = pygame.font.SysFont("Monospace", 22)

        self.alpha_bird = pygame.Surface((20, 20))
        self.alpha_bird.set_alpha(128)
        self.alpha_bird.fill((255, 0, 0))

    def get_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return None
        return events

    def get_pressed(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            return True
        return False

    def draw_state(self, state, frame=None, secondary_states=None):
        self.screen.fill((0, 0, 0))

        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            pygame.Rect(
                20 + 480 * (state["next_dist"] - self.pipe_width) + 10,
                480 - 480 * (state["next_height"] + self.gap_half_height) - 1000 - 10,
                480 * self.pipe_width - 20,
                1000,
            ),
        )
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            pygame.Rect(
                20 + 480 * (state["next_dist"] - self.pipe_width) + 10,
                480 - 480 * (state["next_height"] - self.gap_half_height) + 10,
                480 * self.pipe_width - 20,
                1000,
            ),
        )

        if secondary_states is not None:
            for s_state in secondary_states:
                if s_state is None:
                    continue
                pygame.draw.rect(
                    self.screen,
                    (0, 0, 255),
                    pygame.Rect(10, 480 - 480 * s_state["height"] - 10, 20, 20),
                )
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            pygame.Rect(10, 480 - 480 * state["height"] - 10, 20, 20),
        )

        if frame:
            text_surface = self.frame_font.render(str(frame), False, (255, 255, 255))
            self.screen.blit(text_surface, (500, 0))

        y = 50
        ystep = 60

        h = state["height"]
        text_surface = self.debug_font.render(
            f"height =\n{h:.3f} ", False, (255, 255, 255)
        )
        self.screen.blit(text_surface, (500, y))
        y += ystep

        s = state["speed"]
        text_surface = self.debug_font.render(
            f"speed =\n{s:.6f} ", False, (255, 255, 255)
        )
        self.screen.blit(text_surface, (500, y))
        y += ystep

        v = state["vert_vel"]
        text_surface = self.debug_font.render(
            f"vert_vel =\n{v:+.5f} ", False, (255, 255, 255)
        )
        self.screen.blit(text_surface, (500, y))
        y += ystep

        d = state["next_dist"]
        text_surface = self.debug_font.render(
            f"next_dist =\n{d:.3f} ", False, (255, 255, 255)
        )
        self.screen.blit(text_surface, (500, y))
        y += ystep

        h = state["next_height"]
        text_surface = self.debug_font.render(
            f"next_height =\n{h:.3f} ", False, (255, 255, 255)
        )
        self.screen.blit(text_surface, (500, y))
        y += ystep + 20

        f = state["frame"]
        text_surface = self.debug_font.render(
            f"frame =\n{f} ", False, (255, 255, 255)
        )
        self.screen.blit(text_surface, (500, y))
        y += ystep

        li = state["last_input"]
        text_surface = self.debug_font.render(
            f"last_input =\n{li} ", False, (255, 255, 255)
        )
        self.screen.blit(text_surface, (500, y))

        pygame.display.flip()
        self.fpsClock.tick(self.fps)
