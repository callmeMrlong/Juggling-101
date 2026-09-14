import pygame

class ClownAnimator:
    """Handles clown animation playback for juggling sequences"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.is_playing = False
        self.animation_time = 0.0
        self.sequence = []
        self.base_hand_power = {"Q": 0.0, "E": 0.0}
        self.countdown = 0.0
        self.countdown_total = 5.0
        self.font = pygame.font.SysFont("Arial", 48, bold=True)
        
        # Clown properties
        self.clown_pos = (width // 2, height // 2)
        self.clown_radius = 40
        self.clown_color = (255, 100, 50)  # Orange
        
        # Hand positions (Q = Left, E = Right)
        self.hand_positions = {
            "Q": (self.clown_pos[0] - 80, self.clown_pos[1] + 60),  # Left hand
            "E": (self.clown_pos[0] + 80, self.clown_pos[1] + 60)   # Right hand
        }
        
        # Ball tracking during animation
        self.animated_balls = {}  # ball -> {"pos": (x, y), "in_hand": bool}
    
    def start_animation(self, sequence, base_hand_power):
        """Start a new animation with the given sequence"""
        self.sequence = sequence
        self.base_hand_power = base_hand_power
        self.countdown = self.countdown_total
        self.is_playing = False
        self.animation_time = 0.0
        self.animated_balls = {}
        print(f"Clown animation ready: {sequence}")
    
    def update(self, dt):
        """Update animation state"""
        if self.countdown > 0:
            self.countdown -= dt
            if self.countdown <= 0:
                self.is_playing = True
                self.animation_time = 0.0
                self.initialize_balls()
        
        if self.is_playing:
            self.animation_time += dt
            self.update_ball_positions()
            
            # Check if animation is complete
            if self.animation_time > self.get_total_animation_duration():
                self.is_playing = False
    
    def initialize_balls(self):
        """Initialize balls at the hands for animation start"""
        # Start with all 3 balls (A, D, S) distributed across hands based on sequence start
        self.animated_balls = {
            "A": {"pos": list(self.hand_positions["E"]), "in_hand": True, "countdown": 0},
            "S": {"pos": list(self.hand_positions["E"]), "in_hand": True, "countdown": 0},
            "D": {"pos": list(self.hand_positions["Q"]), "in_hand": True, "countdown": 0}
        }
    
    def update_ball_positions(self):
        """Update positions of balls based on sequence and timing"""
        # Track which balls are in flight and their countdowns
        for move in self.sequence:
            ball = move[0]
            target_hand = move[1]
            height_modifier = self.count_height_modifiers(move)
            
            # Calculate when this throw happens and when it lands
            throw_time = self.get_throw_time_for_move(move)
            land_time = self.get_land_time_for_move(move)
            
            if throw_time <= self.animation_time < land_time:
                # Ball is in flight
                progress = (self.animation_time - throw_time) / (land_time - throw_time)
                
                # Get throwing hand and target hand positions
                throw_hand = self.get_throwing_hand_for_move(move)
                start_pos = self.hand_positions[throw_hand]
                end_pos = self.hand_positions[target_hand]
                
                # Parabolic trajectory
                x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
                y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
                
                # Add arc based on height modifier
                arc_height = 100 + (50 * height_modifier)
                y -= arc_height * (1 - (progress * 2 - 1) ** 2)
                
                self.animated_balls[ball]["pos"] = [x, y]
                self.animated_balls[ball]["in_hand"] = False
            
            elif self.animation_time >= land_time:
                # Ball is in hand
                self.animated_balls[ball]["pos"] = list(self.hand_positions[target_hand])
                self.animated_balls[ball]["in_hand"] = True
            elif self.animation_time < throw_time:
                # Ball hasn't been thrown yet
                if ball in self.animated_balls:
                    # Keep ball in its current hand
                    pass
    
    def get_throw_time_for_move(self, move):
        """Calculate when a move starts (ball is thrown)"""
        move_index = self.sequence.index(move)
        time = 0.0
        
        for i in range(move_index):
            prev_move = self.sequence[i]
            land_time = self.get_land_time_for_move(prev_move)
            if i == move_index - 1:
                time = land_time
        
        return time
    
    def get_land_time_for_move(self, move):
        """Calculate when a ball lands (move completes)"""
        ball = move[0]
        target_hand = move[1]
        height_modifier = self.count_height_modifiers(move)
        
        # Find this move's index
        move_index = self.sequence.index(move)
        time = 0.0
        
        for i in range(move_index + 1):
            move_str = self.sequence[i]
            ball_letter = move_str[0]
            hand_letter = move_str[1]
            height_mod = self.count_height_modifiers(move_str)
            
            # Flight duration = base_power + 1.0 + (0.5 * height_modifier)
            duration = self.base_hand_power[hand_letter] + 1.0 + (abs(height_mod) * 0.5)
            time += duration
        
        return time
    
    def get_total_animation_duration(self):
        """Get total duration of the animation"""
        if not self.sequence:
            return 0.0
        
        total_time = 0.0
        for move in self.sequence:
            target_hand = move[1]
            height_modifier = self.count_height_modifiers(move)
            duration = self.base_hand_power[target_hand] + 1.0 + (abs(height_modifier) * 0.5)
            total_time += duration
        
        return total_time
    
    def count_height_modifiers(self, move):
        """Count W and X characters to determine height modifier"""
        height_count = move.count('W') - move.count('X')
        return height_count
    
    def get_throwing_hand_for_move(self, move):
        """Determine which hand threw the ball"""
        ball = move[0]
        target_hand = move[1]
        
        # If this is the first move of the sequence, determine from initial state
        if move == self.sequence[0]:
            # Assume it comes from the opposite hand of target
            return "Q" if target_hand == "E" else "E"
        
        # Otherwise, it comes from the hand that caught it in the previous move
        prev_move = self.sequence[self.sequence.index(move) - 1]
        if prev_move[0] == ball:
            return prev_move[1]
        
        # If ball wasn't in previous move, find where it came from
        for i in range(self.sequence.index(move) - 1, -1, -1):
            if self.sequence[i][0] == ball:
                return self.sequence[i][1]
        
        return "Q"  # Default fallback
    
    def draw(self, screen):
        """Draw the clown and animated balls"""
        if self.countdown > 0:
            # Draw countdown timer
            countdown_text = self.font.render(f"{int(self.countdown) + 1}", True, (255, 255, 255))
            text_rect = countdown_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 100))
            screen.blit(countdown_text, text_rect)
        
        if self.is_playing:
            # Draw clown head
            pygame.draw.circle(screen, self.clown_color, self.clown_pos, self.clown_radius)
            
            # Draw clown face
            eye_offset = 15
            pygame.draw.circle(screen, (0, 0, 0), 
                             (self.clown_pos[0] - eye_offset, self.clown_pos[1] - 10), 5)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (self.clown_pos[0] + eye_offset, self.clown_pos[1] - 10), 5)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (self.clown_pos[0], self.clown_pos[1] + 15), 8)
            
            # Draw hands
            pygame.draw.circle(screen, self.clown_color, self.hand_positions["Q"], 15)
            pygame.draw.circle(screen, self.clown_color, self.hand_positions["E"], 15)
            
            # Draw animated balls
            for ball, data in self.animated_balls.items():
                ball_colors = {"A": (230, 57, 70), "S": (58, 125, 68), "D": (67, 97, 238)}
                color = ball_colors.get(ball, (255, 255, 255))
                
                pos = tuple(int(p) for p in data["pos"])
                radius = 20 if data["in_hand"] else 15
                pygame.draw.circle(screen, color, pos, radius)
                
                # Draw ball label
                small_font = pygame.font.SysFont("Arial", 12, bold=True)
                label = small_font.render(ball, True, (255, 255, 255))
                label_rect = label.get_rect(center=pos)
                screen.blit(label, label_rect)
