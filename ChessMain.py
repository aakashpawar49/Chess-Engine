import pygame as p
import ChessEngine, ChessAI
import sys
from multiprocessing import Process, Queue

# Constants - Increased board size
BOARD_WIDTH = BOARD_HEIGHT = 700  # Increased from 552
MOVE_LOG_PANEL_WIDTH = 300  # Increased from 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Background colors
BG_COLOR = p.Color(40, 44, 52)  # Dark slate color for background
MOVE_LOG_BG_COLOR = p.Color(30, 34, 42)  # Slightly darker for move log

# Load Images
def loadImages():
    """
    Initialize a global dictionary of images.
    This will be called exactly once in the main.
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

# Draw button function
def drawButton(screen, text, rect, color, hover_color, font):
    mouse_pos = p.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    p.draw.rect(screen, hover_color if is_hovered else color, rect)
    label = font.render(text, True, p.Color("white"))
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    return is_hovered

# Show start screen for game mode selection
def showStartScreen(screen):
    font = p.font.SysFont("Helvetica", 42, True, True)
    button_font = p.font.SysFont("Helvetica", 32)
    
    # Center buttons on the larger screen
    button_width = 340
    button_height = 80
    screen_center_x = (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH) // 2
    
    button1_rect = p.Rect(
        screen_center_x - button_width // 2,
        250,
        button_width,
        button_height
    )
    
    button2_rect = p.Rect(
        screen_center_x - button_width // 2,
        350,
        button_width,
        button_height
    )
    
    button3_rect = p.Rect(
        screen_center_x - button_width // 2,
        450,
        button_width,
        button_height
    )
    
    player_one = True  # Default to human playing white
    player_two = False  # Default to AI playing black
    selecting = True
    
    # Create a subtle pattern background
    pattern = p.Surface((20, 20))
    pattern.fill(BG_COLOR)
    p.draw.rect(pattern, p.Color(50, 54, 62), p.Rect(0, 0, 10, 10))
    p.draw.rect(pattern, p.Color(50, 54, 62), p.Rect(10, 10, 10, 10))
    
    while selecting:
        # Fill with pattern
        for y in range(0, screen.get_height(), 20):
            for x in range(0, screen.get_width(), 20):
                screen.blit(pattern, (x, y))
        
        # Draw a decorative header
        header_rect = p.Rect(0, 0, BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, 120)
        p.draw.rect(screen, p.Color(25, 29, 37), header_rect)
        p.draw.line(screen, p.Color(60, 64, 72), (0, 120), (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, 120), 3)
        
        # Title with shadow effect
        title_shadow = font.render("Chess Game", True, p.Color(30, 30, 30))
        title = font.render("Chess Game", True, p.Color(220, 220, 220))
        screen.blit(title_shadow, (screen_center_x - title.get_width() // 2 + 2, 32))
        screen.blit(title, (screen_center_x - title.get_width() // 2, 30))
        
        subtitle = p.font.SysFont("Helvetica", 28).render("Select Game Mode", True, p.Color(180, 180, 180))
        screen.blit(subtitle, (screen_center_x - subtitle.get_width() // 2, 160))
        
        # Draw buttons with nicer colors
        hover1 = drawButton(screen, "1 Player (vs AI)", button1_rect, 
                           p.Color(70, 130, 180), p.Color(90, 150, 200), button_font)
        hover2 = drawButton(screen, "2 Players", button2_rect, 
                           p.Color(70, 130, 180), p.Color(90, 150, 200), button_font)
        hover3 = drawButton(screen, "AI vs AI", button3_rect,
                           p.Color(70, 130, 180), p.Color(90, 150, 200), button_font)
        
        p.display.flip()
        
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if hover1:
                    player_one = True
                    player_two = False
                    selecting = False
                elif hover2:
                    player_one = True
                    player_two = True
                    selecting = False
                elif hover3:
                    player_one = False
                    player_two = False
                    selecting = False
    
    return player_one, player_two

# Main game function
def main():
    """
    The main driver for our code. This will handle user input and update the graphics.
    """
    p.init()
    p.font.init()
    
    # Set window caption
    p.display.set_caption("Chess Game")

    # Initialize screen and clock
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(BG_COLOR)
    
    # Load images before the start screen
    loadImages()
    
    # Show start screen for game mode selection
    player_one, player_two = showStartScreen(screen)
    
    # Initialize game state
    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False
    animate = False
    running = True
    square_selected = ()  # Track last selected square (row, col)
    player_clicks = []  # Track player clicks
    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 16, False, False)  # Slightly larger font
    button_font = p.font.SysFont("Helvetica", 24)
    
    # Center the restart button
    restart_button = p.Rect(
        BOARD_WIDTH // 2 - 80, 
        BOARD_HEIGHT // 2 + 70, 
        160, 
        50
    )

    while running:
        # Fill background with opaque color
        screen.fill(BG_COLOR)
        
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()

            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if game_over:
                    # Check if restart button was clicked
                    mouse_pos = p.mouse.get_pos()
                    if restart_button.collidepoint(mouse_pos):
                        # Reset game and show start screen again
                        player_one, player_two = showStartScreen(screen)
                        game_state = ChessEngine.GameState()
                        valid_moves = game_state.getValidMoves()
                        square_selected = ()
                        player_clicks = []
                        move_made = False
                        animate = False
                        game_over = False
                        if ai_thinking:
                            move_finder_process.terminate()
                            ai_thinking = False
                        move_undone = False
                else:
                    location = p.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, col) or col >= 8:  # User clicked the same square twice or outside board
                        square_selected = ()  # Deselect
                        player_clicks = []  # Clear clicks
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)
                    if len(player_clicks) == 2 and human_turn:  # After second click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # Reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]

            # Key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r:  # Reset the game when 'r' is pressed
                    player_one, player_two = showStartScreen(screen)
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

        # AI move finder
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()  # Used to pass data between threads
                move_finder_process = Process(target=ChessAI.findBestMove, args=(game_state, valid_moves, return_queue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ChessAI.findRandomMove(valid_moves)
                game_state.makeMove(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False

        drawGameState(screen, game_state, valid_moves, square_selected)

        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)
        else:
            # Draw restart button with better styling
            drawButton(screen, "Play Again", restart_button, 
                      p.Color(40, 120, 200), p.Color(60, 140, 220), button_font)

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


# Function to draw the game state
def drawGameState(screen, game_state, valid_moves, square_selected):
    # Draw a border around the board
    board_border = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT)
    p.draw.rect(screen, p.Color(20, 20, 20), board_border, 4)
    
    drawBoard(screen)  # Draw squares on the board
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)  # Draw pieces on top


def drawBoard(screen):
    # Using more appealing colors for the board
    colors = [p.Color(240, 240, 210), p.Color(118, 150, 86)]  # Light cream and forest green
    
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
    # Draw coordinates around the board
    coord_font = p.font.SysFont("Arial", 16)
    for i in range(DIMENSION):
        # Draw row numbers (8 to 1)
        num = coord_font.render(str(8-i), True, p.Color(200, 200, 200))
        screen.blit(num, (BOARD_WIDTH - 15, i * SQUARE_SIZE + 5))
        
        # Draw column letters (a to h)
        letter = coord_font.render(chr(97 + i), True, p.Color(200, 200, 200))
        screen.blit(letter, (i * SQUARE_SIZE + 5, BOARD_HEIGHT - 20))


def highlightSquares(screen, game_state, valid_moves, square_selected):
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color(100, 255, 100))  # Brighter green
        screen.blit(s, (last_move.end_col * SQUARE_SIZE, last_move.end_row * SQUARE_SIZE))

    if square_selected != ():
        row, col = square_selected
        if row < 8 and col < 8 and game_state.board[row][col][0] == ('w' if game_state.white_to_move else 'b'):
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(120)
            s.fill(p.Color(30, 144, 255))  # Dodger blue
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            
            # Highlight valid moves with a more visible indicator
            s.fill(p.Color(255, 215, 0))  # Gold color
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    # Draw a circle in the center of the square for valid moves
                    p.draw.circle(screen, p.Color(255, 215, 0, 150),
                                 (move.end_col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                  move.end_row * SQUARE_SIZE + SQUARE_SIZE // 2),
                                 SQUARE_SIZE // 4)


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawMoveLog(screen, game_state, font):
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, MOVE_LOG_BG_COLOR, move_log_rect)
    
    # Add a gradient header for the move log
    header_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, 40)
    p.draw.rect(screen, p.Color(50, 60, 70), header_rect)
    p.draw.line(screen, p.Color(100, 100, 100), 
               (BOARD_WIDTH, 40), (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, 40), 1)
    
    title_font = p.font.SysFont("Arial", 24, True, False)
    title_text = title_font.render("Move Log", True, p.Color('white'))
    screen.blit(title_text, move_log_rect.move(15, 8))

    # Status indicator - whose turn it is
    turn_text = "White's Turn" if game_state.white_to_move else "Black's Turn"
    turn_color = p.Color(220, 220, 220) if game_state.white_to_move else p.Color(100, 100, 100)
    turn_font = p.font.SysFont("Arial", 18)
    turn_label = turn_font.render(turn_text, True, turn_color)
    screen.blit(turn_label, (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH - turn_label.get_width() - 15, 12))

    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = f"{i // 2 + 1}. {str(move_log[i])}"
        if i + 1 < len(move_log):
            move_string += f"  {str(move_log[i + 1])}"
        move_texts.append(move_string)

    # Improved move log formatting
    moves_per_row = 1  # One move pair per row for better readability
    padding = 15
    line_spacing = 8
    text_y = 50  # Start below the header
    
    # Alternating row colors for better readability
    for i, move_text in enumerate(move_texts):
        row_color = p.Color(45, 49, 57) if i % 2 == 0 else p.Color(40, 44, 52)
        row_rect = p.Rect(BOARD_WIDTH, text_y, MOVE_LOG_PANEL_WIDTH, font.get_height() + line_spacing)
        p.draw.rect(screen, row_color, row_rect)
        
        text_object = font.render(move_text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y + line_spacing // 2)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing

    # Draw a subtle border around move log
    p.draw.rect(screen, p.Color(80, 80, 80), move_log_rect, 1)


def drawEndGameText(screen, text):
    # Create a more stylish end game overlay
    overlay = p.Surface((BOARD_WIDTH, BOARD_HEIGHT))
    overlay.set_alpha(210)  # More opaque
    
    # Gradient effect
    for i in range(100):
        p.draw.rect(overlay, p.Color(20 + i//10, 20 + i//10, 30 + i//10), 
                   p.Rect(0, i*(BOARD_HEIGHT//100), BOARD_WIDTH, BOARD_HEIGHT//100))
    
    screen.blit(overlay, (0, 0))

    # Text with better styling
    font = p.font.SysFont("Arial", 48, True, False)
    text_object = font.render(text, True, p.Color(220, 220, 220))
    shadow_object = font.render(text, True, p.Color(40, 40, 40))

    # Add a decorative background behind the text
    text_bg = p.Rect(
        BOARD_WIDTH // 2 - text_object.get_width() // 2 - 20,
        BOARD_HEIGHT // 2 - text_object.get_height() // 2 - 50,
        text_object.get_width() + 40,
        text_object.get_height() + 30
    )
    p.draw.rect(screen, p.Color(30, 30, 40, 200), text_bg)
    p.draw.rect(screen, p.Color(80, 80, 100), text_bg, 2)

    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH // 2 - text_object.get_width() // 2,
        BOARD_HEIGHT // 2 - text_object.get_height() // 2 - 35  # Moved up to make space for the button
    )

    # Draw text with shadow for better visibility
    screen.blit(shadow_object, text_location.move(3, 3))
    screen.blit(text_object, text_location)


def animateMove(move, screen, board, clock):
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    
    for frame in range(frame_count + 1):
        # Fill background for each frame
        screen.fill(BG_COLOR)
        
        row, col = (move.start_row + d_row * frame / frame_count, 
                    move.start_col + d_col * frame / frame_count)
        
        drawBoard(screen)
        drawPieces(screen, board)
        
        # Colors for the destination square
        color = p.Color(240, 240, 210) if (move.end_row + move.end_col) % 2 == 0 else p.Color(118, 150, 86)
        
        end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        
        # Show captured piece
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        
        # Draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        p.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()