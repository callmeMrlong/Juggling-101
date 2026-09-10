import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juggling 101")
clock = pygame.time.Clock()

# Initialize Font for Labels
font = pygame.font.SysFont("Arial", 24, bold=True)
countdown_font = pygame.font.SysFont("Arial", 72, bold=True)
streak_font = pygame.font.SysFont("Arial", 48, bold=True)
held_ball_font = pygame.font.SysFont("Arial", 16, bold=True)

# Load hand textures
try:
    left_hand_img = pygame.image.load("textures/left.png")
    right_hand_img = pygame.image.load("textures/right.png")
    # Scale hands to fit nicely in corners
    left_hand_img = pygame.transform.scale(left_hand_img, (120, 120))
    right_hand_img = pygame.transform.scale(right_hand_img, (120, 120))
except pygame.error as e:
    print(f"Error loading hand textures: {e}")
    left_hand_img = None
    right_hand_img = None

# Ball Visual Data (Positions and Colors)
balls_gui = {
    "A": {"pos": (200, 150), "color": (230, 57, 70)},  # Red Ball
    "S": {"pos": (400, 150), "color": (58, 125, 68)},  # Green Ball
    "D": {"pos": (600, 150), "color": (67, 97, 238)}  # Blue Ball
}

# Ball state tracking for countdowns
ball_countdowns = {
    "A": {"countdown": 0, "max_countdown": 0, "landing_hand": None},
    "S": {"countdown": 0, "max_countdown": 0, "landing_hand": None},
    "D": {"countdown": 0, "max_countdown": 0, "landing_hand": None}
}

# VARS
current_ball = None
target_hand = None
height_diff = ""  # W (up), X (down), or empty
throw_type = ""  # Z (inside), C (outside)
sequence = []
height_modifier = 0
streak = 0

# Hand mapping: Q is Left, E is Right
hands = {"Q": {"D": "in_hand"}, "E": {"A": "in_hand", "S": "in_hand"}}

# MAIN LOOP
running = True
while running:
    screen.fill((30, 30, 30))

    # --- DRAW HAND TEXTURES ---
    if left_hand_img:
        screen.blit(left_hand_img, (10, HEIGHT - 130))
    if right_hand_img:
        screen.blit(right_hand_img, (WIDTH - 130, HEIGHT - 130))

    # --- DRAW BALLS GUI ---
    for label, info in balls_gui.items():
        # Draw the ball normally (radius 70) at its default position
        pygame.draw.circle(screen, info["color"], info["pos"], 70)

        # Draw countdown if active
        if ball_countdowns[label]["countdown"] > 0:
            countdown_text = countdown_font.render(f"{ball_countdowns[label]['countdown']:.2f}", True, (255, 255, 255))
            countdown_rect = countdown_text.get_rect(center=info["pos"])
            screen.blit(countdown_text, countdown_rect)

        # Render and draw the text label above the ball
        text_surface = font.render(label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(info["pos"][0], info["pos"][1] - 85))
        screen.blit(text_surface, text_rect)

    # --- DRAW HELD BALLS IN HANDS ---
    for hand, balls_dict in hands.items():
        held_balls = [ball for ball, state in balls_dict.items() if state == "in_hand"]

        if held_balls:
            # Determine hand position: Q is Left, E is Right
            if hand == "Q":  # Left hand
                base_x, base_y = 60, HEIGHT - 70
            else:  # Right hand (E)
                base_x, base_y = WIDTH - 60, HEIGHT - 70

            # Add offsets for multiple balls in same hand
            for idx, ball in enumerate(held_balls):
                offset_x = idx * 30 - (len(held_balls) - 1) * 15  # Center the group
                offset_y = idx * 20
                held_pos = (base_x + offset_x, base_y + offset_y)

                ball_info = balls_gui[ball]
                held_ball_radius = 20

                # Draw the smaller held ball
                pygame.draw.circle(screen, ball_info["color"], held_pos, held_ball_radius)

                # Draw the letter inside the held ball
                letter_surface = held_ball_font.render(ball, True, (255, 255, 255))
                letter_rect = letter_surface.get_rect(center=held_pos)
                screen.blit(letter_surface, letter_rect)

    # Draw streak counter at top of screen
    streak_text = streak_font.render(f"Streak: {streak}", True, (255, 215, 0))
    streak_rect = streak_text.get_rect(center=(WIDTH // 2, 30))
    screen.blit(streak_text, streak_rect)

    # Update countdowns and handle ball landing
    for ball in ball_countdowns:
        if ball_countdowns[ball]["countdown"] > 0:
            ball_countdowns[ball]["countdown"] -= 1 / 60  # Decrease by frame time (assuming 60 FPS)

            # If countdown just finished, move ball to landing hand
            if ball_countdowns[ball]["countdown"] <= 0 and ball_countdowns[ball]["landing_hand"] is not None:
                landing_hand = ball_countdowns[ball]["landing_hand"]
                # Remove ball from all hands first
                for hand in hands:
                    if ball in hands[hand]:
                        hands[hand][ball] = "in_air"
                # Add ball to landing hand
                hands[landing_hand][ball] = "in_hand"
                ball_countdowns[ball]["landing_hand"] = None

                # Check streak condition after ball lands
                total_held = sum(1 for h in hands for b in hands[h] if hands[h][b] == "in_hand")
                if total_held >= 2:
                    streak = 0
                    print(f"Streak broken! 2 or more balls held.")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # 1. Declare Ball: A, S, D
            if event.key in [pygame.K_a, pygame.K_s, pygame.K_d]:
                current_ball = pygame.key.name(event.key).upper()
                print(f"Selected ball: {current_ball}")

            # 2. Declare Target Hand: Q (Left), E (Right) - where the ball will be thrown TO
            elif event.key in [pygame.K_q, pygame.K_e] and current_ball:
                target_hand = pygame.key.name(event.key).upper()
                print(f"Target hand: {target_hand}")

            # 3. Change Height (Optional): W (up), X (down) - Multi-press allowed
            elif event.key == pygame.K_w and target_hand:
                height_modifier += 1
                print(f"Height increased! Current modifier: {height_modifier:+d}")

            elif event.key == pygame.K_x and target_hand:
                height_modifier -= 1
                print(f"Height decreased! Current modifier: {height_modifier:+d}")

            # 4. Throw Type (Finish sequence): Z (Inside), C (Outside)
            elif event.key in [pygame.K_z, pygame.K_c] and target_hand:
                throw_type = pygame.key.name(event.key).upper()

                # Format height output: display empty if 0, otherwise show the total count (e.g., WW or XX)
                if height_modifier > 0:
                    height_str = "W" * height_modifier
                elif height_modifier < 0:
                    height_str = "X" * abs(height_modifier)
                else:
                    height_str = ""

                # Complete the sequence string
                move = f"{current_ball}{target_hand}{height_str}{throw_type}"
                sequence.append(move)
                print(f"Sequence: {sequence}")

                # The landing hand is the target hand specified in the sequence
                landing_hand = target_hand

                # Set countdown for the thrown ball based on height modifier
                # Base countdown of 1 second, plus 0.5 seconds per height level
                countdown_duration = 1.0 + (abs(height_modifier) * 0.5)
                ball_countdowns[current_ball]["countdown"] = countdown_duration
                ball_countdowns[current_ball]["max_countdown"] = countdown_duration
                ball_countdowns[current_ball]["landing_hand"] = landing_hand

                # Remove ball from all hands (throw it)
                for hand in hands:
                    if current_ball in hands[hand]:
                        hands[hand][current_ball] = "in_air"

                # Increment streak by 1 for this sequence
                streak += 1
                print(f"Sequence completed! Streak: {streak}")

                # Check if 2 or more balls are held
                total_held = sum(1 for h in hands for b in hands[h] if hands[h][b] == "in_hand")
                if total_held >= 2:
                    streak = 0
                    print(f"Streak broken! 2 or more balls held.")

                # Reset for next throw
                current_ball = None
                target_hand = None
                height_diff = ""
                throw_type = ""
                height_modifier = 0

    pygame.display.flip()
    clock.tick(60)

pygame.quit()