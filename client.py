import pygame, sys, sockets, socket
pygame.init()


class Player:
    def __init__(self, coords, color):
        self.coords = coords
        self.color = color

    def control_handler(self, k):
        if k[pygame.K_w]:
            self.coords[1] -= 0.2
        elif k[pygame.K_s]:
            self.coords[1] += 0.2

        if k[pygame.K_a]:
            self.coords[0] -= 0.2
        elif k[pygame.K_d]:
            self.coords[0] += 0.2

    def update(self, surf):
        pygame.draw.rect(surf, self.color, (*self.coords, 20, 20))



screen = pygame.display.set_mode((500, 500))
player = Player([250, 250], (255, 0, 0))
client_sock = sockets.Client((socket.gethostname(), 8080))

while True:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    client_sock.send("r:coords;")
    client_sock.event_handler()


    player.coords = client_sock.state.get("coords", [250, 250])
    screen.fill((0, 0, 0))
    player.update(screen)

    pygame.display.update()
    

