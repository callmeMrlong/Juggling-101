import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juggling 101")
clock = pygame.time.Clock()

# Initialize Font for Labels
font = pygame.font.SysFont("Arial", 24, bold=True)

# Ball Visual Data (Positions and Colors)
balls_gui = {
    "A": {"pos": (300, 150), "color": (230, 57, 70)},    # Red Ball
    "S": {"pos": (400, 150), "color": (58, 125, 68)},    # Green Ball
    "D": {"pos": (500, 150), "color": (67, 97, 238)}     # Blue Ball
}


#VARS
current_ball = None
current_hand = None
height_diff = ""  # W (up), X (down), or empty
throw_type = ""  # Z (inside), C (outside)
sequence = []
height_modifier = 0

# Hand mapping: Q is Left, E is Right
hands = {"Q": {"D": "in_hand"}, "E": {"A": "in_hand", "S": "in_hand"}}



#MAIN LOOP
running = True
while running:
  screen.fill((30, 30, 30))

    # --- DRAW BALLS GUI ---
  for label, info in balls_gui.items():
        # Draw the ball (increased radius from 25 to 40)
        pygame.draw.circle(screen, info["color"], info["pos"], 40)

        # Render and draw the text label above the ball
        text_surface = font.render(label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(info["pos"][0], info["pos"][1] - 55))
        screen.blit(text_surface, text_rect)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    elif event.type == pygame.KEYDOWN:
      # 1. Declare Ball: A, S, D
      if event.key in [pygame.K_a, pygame.K_s, pygame.K_d]:
        current_ball = pygame.key.name(event.key).upper()

      # 2. Declare Hand: Q (Left), E (Right)
      elif event.key in [pygame.K_q, pygame.K_e] and current_ball:
        current_hand = pygame.key.name(event.key).upper()

      # 3. Change Height (Optional): W (up), X (down) - Multi-press allowed
      elif event.key == pygame.K_w and current_hand:
        height_modifier += 1
        print(f"Height increased! Current modifier: {height_modifier:+d}")

      elif event.key == pygame.K_x and current_hand:
        height_modifier -= 1
        print(f"Height decreased! Current modifier: {height_modifier:+d}")

      # 4. Throw Type (Finish sequence): Z (Inside), C (Outside)
      elif event.key in [pygame.K_z, pygame.K_c] and current_hand:
        throw_type = pygame.key.name(event.key).upper()

        # Format height output: display empty if 0, otherwise show the total count (e.g., WW or XX)
        if height_modifier > 0:
            height_str = "W" * height_modifier
        elif height_modifier < 0:
            height_str = "X" * abs(height_modifier)
        else:
            height_str = ""

        # Complete the sequence string
        move = f"{current_ball}{current_hand}{height_str}{throw_type}"
        sequence.append(move)
        print(sequence)


        # Reset for next throw
        current_ball = None
        current_hand = None
        height_diff = ""
        throw_type = ""
        height_modifier = 0

  pygame.display.flip()
  clock.tick(60)

pygame.quit()
