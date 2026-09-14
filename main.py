import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juggling 101")
clock = pygame.time.Clock()

# Initialize Font for Labels
font = pygame.font.SysFont("Arial", 24, bold=True)
small_font = pygame.font.SysFont("Arial", 16, bold=True)
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

# Settings
show_settings = True
require_throw_type = True
hand_power = {"Q": 0.0, "E": 0.0}
base_hand_power = {"Q": 0.0, "E": 0.0}  # Stores base power throughout the game
editing_hand = None  # "Q" or "E" for which hand power is being edited
power_input = ""

# Hand mapping: Q is Left, E is Right
hands = {"Q": {"D": "in_hand"}, "E": {"A": "in_hand", "S": "in_hand"}}

def draw_settings_menu():
    """Draw the settings menu overlay"""
    # Semi-transparent background
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Settings title
    title = font.render("Settings", True, (255, 255, 255))
    title_rect = title.get_rect(center=(WIDTH // 2, 50))
    screen.blit(title, title_rect)
    
    # Left hand power
    left_label = small_font.render("Left Hand (Q) Power:", True, (255, 255, 255))
    screen.blit(left_label, (50, 120))
    
    # Input box for left hand
    left_input_rect = pygame.Rect(50, 160, 150, 40)
    pygame.draw.rect(screen, (255, 255, 255), left_input_rect, 2)
    if editing_hand == "Q":
        pygame.draw.rect(screen, (100, 200, 255), left_input_rect, 2)
    left_text = small_font.render(str(hand_power["Q"]), True, (255, 255, 255))
    screen.blit(left_text, (left_input_rect.x + 10, left_input_rect.y + 10))
    
    # Plus/Minus buttons for left hand
    left_minus_rect = pygame.Rect(220, 160, 35, 40)
    left_plus_rect = pygame.Rect(260, 160, 35, 40)
    pygame.draw.rect(screen, (200, 200, 200), left_minus_rect)
    pygame.draw.rect(screen, (200, 200, 200), left_plus_rect)
    minus_text = small_font.render("-", True, (0, 0, 0))
    plus_text = small_font.render("+", True, (0, 0, 0))
    screen.blit(minus_text, (left_minus_rect.center[0] - 5, left_minus_rect.center[1] - 10))
    screen.blit(plus_text, (left_plus_rect.center[0] - 5, left_plus_rect.center[1] - 10))
    
    # Right hand power
    right_label = small_font.render("Right Hand (E) Power:", True, (255, 255, 255))
    screen.blit(right_label, (50, 240))
    
    # Input box for right hand
    right_input_rect = pygame.Rect(50, 280, 150, 40)
    pygame.draw.rect(screen, (255, 255, 255), right_input_rect, 2)
    if editing_hand == "E":
        pygame.draw.rect(screen, (100, 200, 255), right_input_rect, 2)
    right_text = small_font.render(str(hand_power["E"]), True, (255, 255, 255))
    screen.blit(right_text, (right_input_rect.x + 10, right_input_rect.y + 10))
    
    # Plus/Minus buttons for right hand
    right_minus_rect = pygame.Rect(220, 280, 35, 40)
    right_plus_rect = pygame.Rect(260, 280, 35, 40)
    pygame.draw.rect(screen, (200, 200, 200), right_minus_rect)
    pygame.draw.rect(screen, (200, 200, 200), right_plus_rect)
    screen.blit(minus_text, (right_minus_rect.center[0] - 5, right_minus_rect.center[1] - 10))
    screen.blit(plus_text, (right_plus_rect.center[0] - 5, right_plus_rect.center[1] - 10))
    
    # Checkbox for throw type requirement
    checkbox_rect = pygame.Rect(50, 380, 20, 20)
    pygame.draw.rect(screen, (255, 255, 255), checkbox_rect, 2)
    if require_throw_type:
        pygame.draw.line(screen, (255, 255, 255), (checkbox_rect.x, checkbox_rect.y), (checkbox_rect.x + 20, checkbox_rect.y + 20), 3)
        pygame.draw.line(screen, (255, 255, 255), (checkbox_rect.x + 20, checkbox_rect.y), (checkbox_rect.x, checkbox_rect.y + 20), 3)
    
    checkbox_label = small_font.render("Require Throw Type (Z/C)", True, (255, 255, 255))
    screen.blit(checkbox_label, (80, 380))
    
    # Start button
    start_button_rect = pygame.Rect(WIDTH // 2 - 75, 480, 150, 50)
    pygame.draw.rect(screen, (100, 150, 100), start_button_rect)
    start_text = font.render("Start Game", True, (255, 255, 255))
    screen.blit(start_text, (start_button_rect.center[0] - 60, start_button_rect.center[1] - 15))
    
    return left_input_rect, right_input_rect, left_minus_rect, left_plus_rect, right_minus_rect, right_plus_rect, checkbox_rect, start_button_rect

# MAIN LOOP
running = True
while running:
    screen.fill((30, 30, 30))

    if show_settings:
        left_input_rect, right_input_rect, left_minus_rect, left_plus_rect, right_minus_rect, right_plus_rect, checkbox_rect, start_button_rect = draw_settings_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Left hand input click
                if left_input_rect.collidepoint(mouse_pos):
                    editing_hand = "Q"
                    power_input = ""
                # Right hand input click
                elif right_input_rect.collidepoint(mouse_pos):
                    editing_hand = "E"
                    power_input = ""
                # Left minus button
                elif left_minus_rect.collidepoint(mouse_pos):
                    hand_power["Q"] = max(0.0, hand_power["Q"] - 0.1)
                    hand_power["Q"] = round(hand_power["Q"], 2)
                # Left plus button
                elif left_plus_rect.collidepoint(mouse_pos):
                    hand_power["Q"] += 0.1
                    hand_power["Q"] = round(hand_power["Q"], 2)
                # Right minus button
                elif right_minus_rect.collidepoint(mouse_pos):
                    hand_power["E"] = max(0.0, hand_power["E"] - 0.1)
                    hand_power["E"] = round(hand_power["E"], 2)
                # Right plus button
                elif right_plus_rect.collidepoint(mouse_pos):
                    hand_power["E"] += 0.1
                    hand_power["E"] = round(hand_power["E"], 2)
                # Checkbox click
                elif checkbox_rect.collidepoint(mouse_pos):
                    require_throw_type = not require_throw_type
                # Start button
                elif start_button_rect.collidepoint(mouse_pos):
                    # Store the base power values for the entire game
                    base_hand_power["Q"] = hand_power["Q"]
                    base_hand_power["E"] = hand_power["E"]
                    show_settings = False
                    editing_hand = None
            elif event.type == pygame.KEYDOWN:
                if editing_hand:
                    if event.key == pygame.K_BACKSPACE:
                        power_input = power_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        try:
                            value = float(power_input) if power_input else 0.0
                            hand_power[editing_hand] = round(max(0.0, value), 2)
                            editing_hand = None
                            power_input = ""
                        except ValueError:
                            power_input = ""
                    elif event.unicode.isdigit() or event.unicode == ".":
                        power_input += event.unicode
    else:
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
                    
                    # If throw type not required, throw immediately
                    if not require_throw_type:
                        # Check if ball is being held by any hand
                        ball_held = False
                        for hand in hands:
                            if current_ball in hands[hand] and hands[hand][current_ball] == "in_hand":
                                ball_held = True
                                break

                        if not ball_held:
                            print(f"Error: Ball {current_ball} is not being held!")
                        else:
                            # Format height output: display empty if 0, otherwise show the total count (e.g., WW or XX)
                            if height_modifier > 0:
                                height_str = "W" * height_modifier
                            elif height_modifier < 0:
                                height_str = "X" * abs(height_modifier)
                            else:
                                height_str = ""

                            # Complete the sequence string (without throw type)
                            move = f"{current_ball}{target_hand}{height_str}"
                            sequence.append(move)
                            print(f"Sequence: {sequence}")

                            # The landing hand is the target hand specified in the sequence
                            landing_hand = target_hand

                            # Set countdown for the thrown ball based on height modifier and base power
                            # Base countdown = base_power + (1.0 + 0.5 * height_modifier)
                            countdown_duration = base_hand_power[target_hand] + 1.0 + (abs(height_modifier) * 0.5)
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

                # 3. Change Height (Optional): W (up), X (down) - Multi-press allowed
                elif event.key == pygame.K_w and target_hand:
                    height_modifier += 1
                    print(f"Height increased! Current modifier: {height_modifier:+d}")

                elif event.key == pygame.K_x and target_hand:
                    height_modifier -= 1
                    print(f"Height decreased! Current modifier: {height_modifier:+d}")

                # 4. Throw Type (Finish sequence): Z (Inside), C (Outside)
                elif event.key in [pygame.K_z, pygame.K_c] and target_hand and require_throw_type:
                    throw_type = pygame.key.name(event.key).upper()

                    # Check if ball is being held by any hand
                    ball_held = False
                    for hand in hands:
                        if current_ball in hands[hand] and hands[hand][current_ball] == "in_hand":
                            ball_held = True
                            break

                    if not ball_held:
                        print(f"Error: Ball {current_ball} is not being held!")
                    else:
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

                        # Set countdown for the thrown ball based on height modifier and base power
                        # Base countdown = base_power + (1.0 + 0.5 * height_modifier)
                        countdown_duration = base_hand_power[target_hand] + 1.0 + (abs(height_modifier) * 0.5)
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
