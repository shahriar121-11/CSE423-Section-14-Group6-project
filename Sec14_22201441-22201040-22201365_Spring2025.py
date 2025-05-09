from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18 
import random
import math
import time

# --- Game Variables ---
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
fovY = 120
game_paused = False
pause_time = 0
camera_pos_list = [0, 2000, 2000]
BATTLEFIELD_SIZE = 5000
BATTLEFIELD_BOUNDS = BATTLEFIELD_SIZE / 2.0
is_day = True
day_color = (0.6, 0.5, 0.3)
night_color = (0.2, 0.2, 0.3)

OVERALL_PLAYER_SCALE = 3.0
PLAYER_HEIGHT = 180 * OVERALL_PLAYER_SCALE
TORSO_LENGTH = 60 * OVERALL_PLAYER_SCALE
LEG_LENGTH = 90 * OVERALL_PLAYER_SCALE
ARM_LENGTH = 70 * OVERALL_PLAYER_SCALE

playerPosition = [0, 0, 0]
playerScore = 0
playerLife = 5000
playerAngle = 0
playerSpeed = 10
playerWin=True
playerTurnSpeed = 5

# Enemy system variables
enemyList = []
enemySpeed = 0.05
MAX_ENEMIES = 100  # Maximum enemies allowed on the battlefield
ENEMY_SPAWN_RATE = 5  # Number of enemies to spawn per second
ENEMY_SPAWN_INTERVAL = 1.0  # Spawn interval in seconds
last_spawn_time = time.time()

ENEMY_TORSO_LENGTH = 60
ENEMY_LEG_LENGTH = 90
ENEMY_ARM_LENGTH = 70
ENEMY_OVERALL_SCALE = 1.5
ENEMY_SHOOT_RANGE = 1500
ENEMY_MIN_SHOOT_INTERVAL_FRAMES = 90
ENEMY_MAX_SHOOT_INTERVAL_FRAMES = 210

Arrows = []
ARROW_SHAFT_LENGTH = 200
ARROW_SHAFT_RADIUS =7.5
ARROW_HEAD_LENGTH = 20
ARROW_HEAD_RADIUS = 15
ARROW_SPEED = 7.5
ARROW_DAMAGE = 1

modeOver = False

# --- AgniAstra Variables ---
activeAgniAstras = [] # Stores active AgniAstra data dictionaries
AgniAstra_RADIUS = 500 # Large AoE
AgniAstra_COLOR = (1.0, 0.4, 0.1) # Orangish-red
AgniAstra_DURATION_FRAMES = 60 # How long the visual effect and damage AoE lasts (e.g., 1 second at 60 FPS)
AgniAstra_COOLDOWN_FRAMES = 1 * 60 # 5 seconds * 60 FPS (approx)
AgniAstra_last_use_frame = -AgniAstra_COOLDOWN_FRAMES # Allow immediate first use
enemiesKilledByAgniAstra = 0
AgniAstra_target_margin = 100 # How far from edge AgniAstras can target

# --- VajraAstra Variables ---
active_VajraAstras = []
VajraAstra_DURATION_FRAMES = 12
VajraAstra_STRIKES_COUNT = 5
VajraAstra_COOLDOWN_FRAMES = 300 # 5 seconds * 60 FPS (approx)
VajraAstra_cooldown_remaining_frames = 0
last_VajraAstra_kill_count = 0

# Frame counter for cooldowns
current_frame_count = 0 

# Brahmastra variables
BRAHMASTRA_COOLDOWN = 60  # 60 seconds cooldown
brahmastra_last_used_time = 0  # Time when Brahmastra was last used
brahmastra_arrow = None  # To track the Brahmastra arrow
brahmastra_state = "ready"  # States: "ready", "firing", "cooldown"
last_frame_time = time.time()  # For delta time calculation

#MAYASTRA VARIABLLES
MAYASTRA_DURATION = 10  # 10 seconds duration
MAYASTRA_COOLDOWN = 40  # 40 seconds cooldown
mayastra_last_used_time = 0  # Time when Mayastra was last used
mayastra_active_until = 0  # When Mayastra effect will end
mayastra_arrow = None  # To track the Mayastra arrow
mayastra_state = "ready"  # States: "ready", "firing", "active", "cooldown"
mayastra_direction_change_interval = 0.2 

#pawan astra vars
PAWAN_ASTRA_ACTIVE = False
PAWAN_ASTRA_TIME = 0
PAWAN_ASTRA_MAX_TIME = 30  # Shorter duration for faster effect
PAWAN_ASTRA_DIRECTION = [0, 1, 0]
PAWAN_ASTRA_HEIGHT = 1000  # Taller effect
PAWAN_ASTRA_WIDTH = 50 

#shield 
SHIELD_ACTIVE = False
SHIELD_TIME = 0
SHIELD_MAX_TIME = 1800  # 
SHIELD_COOLDOWN = 60  #
shield_cooldown_timer = 0

def activate_shield():
    global SHIELD_ACTIVE, SHIELD_TIME, shield_cooldown_timer
    if not SHIELD_ACTIVE and shield_cooldown_timer <= 0:
        SHIELD_ACTIVE = True
        SHIELD_TIME = 0
        print("Shield activated! 5 seconds of protection")

def draw_shield():
    if not SHIELD_ACTIVE:
        return
 
    glPushMatrix()
    glTranslatef(playerPosition[0], playerPosition[1], PLAYER_HEIGHT * 0.5)

    # Pulsing effect based on remaining time
    pulse_intensity = 0.2 * math.sin(SHIELD_TIME * 0.2)  # Pulsing speed
    base_radius = PLAYER_HEIGHT * 0.7
    shield_radius = base_radius * (1.0 + pulse_intensity)
    
    # Main shield sphere (solid blue)
    glColor3f(0.2, 0.5, 1.0)  # Base blue color
    glutSolidSphere(shield_radius, 32, 32)
    
    # Inner glow sphere (lighter blue)
    inner_radius = shield_radius * 0.85
    glColor3f(0.4, 0.7, 1.0)  # Lighter blue
    glutSolidSphere(inner_radius, 32, 32)
    
    # Core sphere (brightest blue)
    core_radius = shield_radius * 0.6
    glColor3f(0.6, 0.9, 1.0)  # Brightest blue
    glutSolidSphere(core_radius, 32, 32)
    
    glPopMatrix()


def update_shield():
    global SHIELD_ACTIVE, SHIELD_TIME, shield_cooldown_timer
    
    if SHIELD_ACTIVE:
        SHIELD_TIME += 1
        if SHIELD_TIME >= SHIELD_MAX_TIME:
            SHIELD_ACTIVE = False
            shield_cooldown_timer = SHIELD_COOLDOWN
            print("Shield deactivated")
    
    if shield_cooldown_timer > 0:
        shield_cooldown_timer -= 1



def draw_pawan_astra():
    if not PAWAN_ASTRA_ACTIVE:
        return
    
    glPushMatrix()
    
    # Thick wind core
    glLineWidth(15.0)
    glBegin(GL_LINES)
    glColor3f(0.5, 0.8, 1.0)  # Bright cyan
    start_x = playerPosition[0]
    start_y = playerPosition[1]
    angle_rad = math.radians(playerAngle)
    end_x = start_x + math.sin(angle_rad) * BATTLEFIELD_BOUNDS
    end_y = start_y + math.cos(angle_rad) * BATTLEFIELD_BOUNDS
    glVertex3f(start_x, start_y, 0)
    glVertex3f(end_x, end_y, 0)
    glEnd()
    
    # Glowing particles
    glPointSize(8.0)
    glBegin(GL_POINTS)
    for i in range(100):  # More particles
        progress = random.random()
        pulse = math.sin(PAWAN_ASTRA_TIME * 0.5 + i) * 0.5 + 0.5  # Pulsing effect
        glColor3f(1, 1, pulse)  # White with pulse
        glVertex3f(
            start_x + (end_x - start_x) * progress + random.uniform(-30, 30),
            start_y + (end_y - start_y) * progress + random.uniform(-30, 30),
            0
        )
    glEnd()
    
    # Area-of-effect indicator
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glColor3f(0.7, 0.9, 1.0)  # Lighter blue
    for angle in [-30, 30]:  # Draw angled lines to show width
        rad = math.radians(playerAngle + angle)
        end_x2 = start_x + math.sin(rad) * BATTLEFIELD_BOUNDS * 0.3
        end_y2 = start_y + math.cos(rad) * BATTLEFIELD_BOUNDS * 0.3
        glVertex3f(start_x, start_y, 0)
        glVertex3f(end_x2, end_y2, 0)
    glEnd()
    
    glPopMatrix()

def kill_enemies_in_pawan_astra_path():
    global enemyList, playerScore
    if not PAWAN_ASTRA_ACTIVE:
        return
    
    # Line start and end points (ground level)
    start_x = playerPosition[0]
    start_y = playerPosition[1]
    
    angle = math.radians(playerAngle)
    end_x = start_x + math.sin(angle) * BATTLEFIELD_BOUNDS
    end_y = start_y + math.cos(angle) * BATTLEFIELD_BOUNDS
    
    # Vector along the Pawan Astra line
    line_vec_x = end_x - start_x
    line_vec_y = end_y - start_y
    line_len = math.sqrt(line_vec_x**2 + line_vec_y**2)
    
    if line_len == 0:
        return
    
    # Check each enemy (only x,y coordinates)
    i = 0
    while i < len(enemyList):
        enemy = enemyList[i]
        ex, ey = enemy['pos'][0], enemy['pos'][1]
        
        # Vector from start to enemy
        enemy_vec_x = ex - start_x
        enemy_vec_y = ey - start_y
        
        # Projection of enemy vector onto line vector
        projection = (enemy_vec_x * line_vec_x + enemy_vec_y * line_vec_y) / line_len
        
        # Clamp projection to line segment
        projection = max(0, min(line_len, projection))
        
        # Closest point on line to enemy
        closest_x = start_x + (line_vec_x * projection) / line_len
        closest_y = start_y + (line_vec_y * projection) / line_len
        
        # Distance from enemy to line (only x,y)
        distance = math.sqrt((ex - closest_x)**2 + (ey - closest_y)**2)
        
        if distance < PAWAN_ASTRA_WIDTH:
            # Kill enemy
            playerScore += 1
            enemyList.pop(i)
        else:
            i += 1

def draw_pawan_astra():
    if not PAWAN_ASTRA_ACTIVE:
        return
    
    glPushMatrix()
    
    # Ground-level wind effect
    glLineWidth(10.0)
    glBegin(GL_LINES)
    glColor3f(0.7, 0.9, 1.0)  # Light blue
    
    # Start at player position
    start_x = playerPosition[0]
    start_y = playerPosition[1]
    
    # Calculate endpoint at battlefield boundary
    angle = math.radians(playerAngle)
    end_x = start_x + math.sin(angle) * BATTLEFIELD_BOUNDS
    end_y = start_y + math.cos(angle) * BATTLEFIELD_BOUNDS
    
    # Draw line at ground level (z=0)
    glVertex3f(start_x, start_y, 0)
    glVertex3f(end_x, end_y, 0)
    glEnd()
    
    # Spark particles
    glPointSize(5.0)
    glBegin(GL_POINTS)
    for i in range(50):
        progress = random.random()
        glColor3f(1, 1, 1)  # White sparks
        glVertex3f(
            start_x + (end_x - start_x) * progress,
            start_y + (end_y - start_y) * progress,
            0
        )
    glEnd()
    glPopMatrix()

def activate_pawan_astra():
    global PAWAN_ASTRA_ACTIVE, PAWAN_ASTRA_TIME
    if not PAWAN_ASTRA_ACTIVE:
        PAWAN_ASTRA_ACTIVE = True
        PAWAN_ASTRA_TIME = 0
        kill_enemies_in_pawan_astra_path()

def kill_enemies_in_pawan_astra_path():
    global enemyList, playerScore
    
    if not PAWAN_ASTRA_ACTIVE:
        return
    
    # Get line segment endpoints (ground level)
    angle_rad = math.radians(playerAngle)
    start_x = playerPosition[0]
    start_y = playerPosition[1]
    end_x = start_x + math.sin(angle_rad) * BATTLEFIELD_BOUNDS
    end_y = start_y + math.cos(angle_rad) * BATTLEFIELD_BOUNDS
    
    # Vector along the line
    line_vec_x = end_x - start_x
    line_vec_y = end_y - start_y
    line_length = math.sqrt(line_vec_x**2 + line_vec_y**2)
    
    if line_length == 0:
        return
    
    # Normalized line direction
    line_dir_x = line_vec_x / line_length
    line_dir_y = line_vec_y / line_length
    
    # Check each enemy
    i = 0
    while i < len(enemyList):
        enemy = enemyList[i]
        ex, ey = enemy['pos'][0], enemy['pos'][1]
        
        # Vector from line start to enemy
        enemy_vec_x = ex - start_x
        enemy_vec_y = ey - start_y
        
        # Projection length of enemy vector onto line
        projection_length = enemy_vec_x * line_dir_x + enemy_vec_y * line_dir_y
        
        # Reject enemies behind player or beyond line end
        if 0 <= projection_length <= line_length:
            # Calculate perpendicular distance
            closest_x = start_x + line_dir_x * projection_length
            closest_y = start_y + line_dir_y * projection_length
            distance = math.sqrt((ex - closest_x)**2 + (ey - closest_y)**2)
            
            if distance < PAWAN_ASTRA_WIDTH:
                playerScore += 1
                enemyList.pop(i)
                continue  # Skip increment since we removed an enemy
        i += 1

def update_pawan_astra():
    global PAWAN_ASTRA_ACTIVE, PAWAN_ASTRA_TIME
    if PAWAN_ASTRA_ACTIVE:
        PAWAN_ASTRA_TIME += 1
        if PAWAN_ASTRA_TIME >= PAWAN_ASTRA_MAX_TIME:
            PAWAN_ASTRA_ACTIVE = False

def pause():
    """Pauses the game by stopping all updates and storing the current time"""
    global game_paused, pause_time, last_frame_time
    if not game_paused:
        game_paused = True
        pause_time = time.time()
        print("Game paused")

def play():
    """Resumes the game from where it was paused"""
    global game_paused, stored_delta_time, last_frame_time, pause_time
    if game_paused:
        game_paused = False
        # Calculate how long we were paused and adjust last_frame_time
        paused_duration = time.time() - pause_time
        last_frame_time += paused_duration
        print("Game resumed") 


def get_delta_time():
    global last_frame_time
    current_time = time.time()
    delta = current_time - last_frame_time
    last_frame_time = current_time
    return delta

def spawnEnemies(num_to_spawn):
    global enemyList, last_spawn_time
    for _ in range(num_to_spawn):
        if len(enemyList) >= MAX_ENEMIES:
            break  # Don't spawn if we've reached max enemies
            
        margin = 200
        x = random.uniform(-BATTLEFIELD_BOUNDS + margin, BATTLEFIELD_BOUNDS - margin)
        y = random.uniform(-BATTLEFIELD_BOUNDS + margin, BATTLEFIELD_BOUNDS - margin)
        z = 0
        min_dist_from_player = 400
        while math.sqrt((x - playerPosition[0])**2 + (y - playerPosition[1])**2) < min_dist_from_player:
            x = random.uniform(-BATTLEFIELD_BOUNDS + margin, BATTLEFIELD_BOUNDS - margin)
            y = random.uniform(-BATTLEFIELD_BOUNDS + margin, BATTLEFIELD_BOUNDS - margin)
        enemyList.append({
            'pos': [x, y, z],
            'angle': 0.0,
            'shoot_timer_frames': random.randint(0, ENEMY_MAX_SHOOT_INTERVAL_FRAMES),
        })

def updateEnemySpawning(delta_time):
    global last_spawn_time
    current_time = time.time()
    
    # Check if it's time to spawn new enemies
    if current_time - last_spawn_time >= ENEMY_SPAWN_INTERVAL:
        # Calculate how many enemies we can spawn (up to MAX_ENEMIES)
        enemies_needed = min(ENEMY_SPAWN_RATE, MAX_ENEMIES - len(enemyList))
        if enemies_needed > 0:
            spawnEnemies(enemies_needed)
        last_spawn_time = current_time


def drawText(x, y, text, font=GLUT_BITMAP_HELVETICA_18): 

    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_bush(x, y): 

    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.1, 0.4, 0.1) if is_day else glColor3f(0.1, 0.3, 0.1)
    gluSphere(gluNewQuadric(), 60, 10, 10)
    glPopMatrix()

def draw_battlefield(): 

    half_size = BATTLEFIELD_BOUNDS
    if is_day:
        glColor3f(*day_color)
    else:
        glColor3f(*night_color)

    glBegin(GL_QUADS)
    glVertex3f(-half_size, -half_size, 0)
    glVertex3f(half_size, -half_size, 0)
    glVertex3f(half_size, half_size, 0)
    glVertex3f(-half_size, half_size, 0)
    glEnd()

    bush_positions = [
        (-1800, -1800), (1800, 1800), (-1800, 1800), (1800, -1800),
        (-1200, -1200), (1200, 1200), (-1200, 1200), (1200, -1200),
        (-800, -800), (800, 800), (-800, 800), (800, -800),
        (-2200, 0), (2200, 0), (0, 2200), (0, -2200)
    ]
    valid_bush_positions = [bp for bp in bush_positions if abs(bp[0]) < half_size and abs(bp[1]) < half_size]
    for bush_x, bush_y in valid_bush_positions:
        draw_bush(bush_x, bush_y)


# --- Player/Enemy Model Drawing Functions ---
def drawLeg(length, silver_armor=False):
    glPushMatrix()
    scale_factor = length / (90.0)
    base_radius_1 = 12.0 * scale_factor
    top_radius_1 = 10.0 * scale_factor
    base_radius_2 = 10.0 * scale_factor
    top_radius_2 = 8.0 * scale_factor
    original_foot_size = 20.0

    if silver_armor: 
        glColor3f(0.8, 0.8, 0.9)
    else: 
        glColor3f(0.6, 0.4, 0.2)
    gluCylinder(gluNewQuadric(), base_radius_1, top_radius_1, length/2.0, 10, 5)
    glTranslatef(0, 0, length/2.0)
    if silver_armor: 
        glColor3f(0.7, 0.7, 0.8)
    gluCylinder(gluNewQuadric(), base_radius_2, top_radius_2, length/2.0, 10, 5)
    glTranslatef(0, 0, length/2.0)
    glColor3f(0.3, 0.2, 0.1)
    glPushMatrix()
    glutSolidCube(original_foot_size)
    glPopMatrix()
    glPopMatrix()

def drawTorso(length):
    glPushMatrix()
    scale_factor = length / (60.0)
    radius = 20.0 * scale_factor
    emblem_radius = 5.0 * scale_factor

    glColor3f(0.85, 0.85, 0.9)
    gluCylinder(gluNewQuadric(), radius, radius, length, 12, 5)

    glColor3f(1.0, 0.84, 0.0)
    glPushMatrix()
    glTranslatef(0, radius * 0.9, length/2.0)
    glutSolidSphere(emblem_radius, 8, 8)
    glPopMatrix()
    glPopMatrix()

def drawHead(radius, helmet=False):
    glPushMatrix()
    original_base_radius = 25.0
    scale_factor = radius / original_base_radius

    glColor3f(0.8, 0.6, 0.4)
    glutSolidSphere(radius, 16, 16)
    if helmet:
        glColor3f(1.0, 0.84, 0.0)
        glPushMatrix()
        helmet_offset_z = (radius * 0.1)
        glTranslatef(0, 0, radius - helmet_offset_z)
        helmet_cyl_radius = radius * 0.9
        helmet_cyl_height = radius * 0.4
        gluCylinder(gluNewQuadric(), helmet_cyl_radius, helmet_cyl_radius, helmet_cyl_height, 12, 2)
        spike_base_radius = radius * 0.06
        spike_height = radius * 0.4
        for i in range(0, 360, 60):
            glPushMatrix()
            glRotatef(i, 0, 0, 1)
            glTranslatef(helmet_cyl_radius * 0.95, 0, helmet_cyl_height * 0.9)
            gluCylinder(gluNewQuadric(), spike_base_radius, 0, spike_height, 6, 1)
            glPopMatrix()
        glPopMatrix()
    glPopMatrix()

def drawArm(length, silver_armor=False):
    glPushMatrix()

    # Rotate to make arm point sideways (along X-axis)
    glRotatef(90, 0, 1, 0)  # Rotate 90 degrees around Y to align Z -> X

    scale_factor = length / 70.0
    base_radius_1 = 10.0 * scale_factor
    top_radius_1 = 8.0 * scale_factor
    base_radius_2 = 8.0 * scale_factor
    top_radius_2 = 6.0 * scale_factor
    hand_sphere_radius = 7.0 * scale_factor

    if silver_armor:
        glColor3f(0.8, 0.8, 0.9)
    else:
        glColor3f(0.7, 0.5, 0.3)

    # Upper arm
    gluCylinder(gluNewQuadric(), base_radius_1, top_radius_1, length / 2.0, 10, 5)

    # Elbow to hand
    glTranslatef(0, 0, length / 2.0)
    if silver_armor:
        glColor3f(0.75, 0.75, 0.85)
    gluCylinder(gluNewQuadric(), base_radius_2, top_radius_2, length / 2.0, 10, 5)

    # Hand sphere
    glTranslatef(0, 0, length / 2.0)
    glColor3f(0.7, 0.5, 0.3)
    glutSolidSphere(hand_sphere_radius, 8, 8)

    glPopMatrix()

def drawIndianBow():
    quad = gluNewQuadric()
    glPushMatrix()

    scale_factor = OVERALL_PLAYER_SCALE

    arc_radius = 40.0 * scale_factor
    segment_length = 5.0 * scale_factor
    cylinder_radius = 1.5 * scale_factor
    segments = 16  # Number of curved arc segments

    # Draw bow arc using small cylinders along a curved arc
    glColor3f(0.6, 0.4, 0.2)
    for i in range(segments):
        theta1 = (i / segments - 0.5) * math.pi  # -π/2 to π/2
        theta2 = ((i + 1) / segments - 0.5) * math.pi

        # Coordinates of segment ends
        x1, y1 = arc_radius * math.cos(theta1), arc_radius * math.sin(theta1)
        x2, y2 = arc_radius * math.cos(theta2), arc_radius * math.sin(theta2)

        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        angle = math.degrees(math.atan2(dy, dx))

        glPushMatrix()
        glTranslatef(x1, y1, 0)
        glRotatef(angle, 0, 0, 1)
        gluCylinder(quad, cylinder_radius, cylinder_radius, length, 8, 1)
        glPopMatrix()

    # Draw central grip
    grip_radius = 5.0 * scale_factor
    glColor3f(0.4, 0.2, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, -cylinder_radius)
    glRotatef(90, 1, 0, 0)  # vertical
    gluCylinder(quad, grip_radius, grip_radius, 5.0 * scale_factor, 8, 1)
    glPopMatrix()

    # Draw bowstring
    glColor3f(0.9, 0.9, 0.8)
    glBegin(GL_LINES)
    glVertex3f(0, arc_radius, 0)
    glVertex3f(0, -arc_radius, 0)
    glEnd()

    glPopMatrix() 


def drawSilverArmor():
    glPushMatrix()
    scale_factor = OVERALL_PLAYER_SCALE
    original_cube_size = 35.0
    size = original_cube_size * scale_factor
    glColor3f(0.85, 0.85, 0.9)
 
    glutSolidCube(size)
    glPopMatrix()

def drawWaistCloth():
    glPushMatrix()
    scale_factor = OVERALL_PLAYER_SCALE
    original_cyl_base_radius = 25.0
    original_cyl_top_radius = 20.0
    original_cyl_height = 35.0
    original_ornament_sphere_radius = 2.0
    original_ornament_translate_radius = 22.0
    cyl_base_radius = original_cyl_base_radius * scale_factor
    cyl_top_radius = original_cyl_top_radius * scale_factor
    cyl_height = original_cyl_height * scale_factor
    ornament_sphere_radius = original_ornament_sphere_radius * scale_factor
    ornament_translate_radius = original_ornament_translate_radius * scale_factor

    glColor3f(0.255, 0.411, 0.882)
    gluCylinder(gluNewQuadric(), cyl_base_radius, cyl_top_radius, cyl_height, 16, 5)
    glColor3f(1.0, 0.84, 0.0)
    for i in range(0, 360, 45):
        glPushMatrix()
        glRotatef(i, 0, 0, 1)
        glTranslatef(ornament_translate_radius, 0, cyl_height * 0.8)
        glutSolidSphere(ornament_sphere_radius, 6, 6)
        glPopMatrix()
    glPopMatrix()

def drawCape():
    glPushMatrix()
    scale_factor = OVERALL_PLAYER_SCALE
    original_top_x = 20.0
    original_top_y_offset = -5.0
    original_bottom_x_spread = 30.0
    original_bottom_y_offset = -10.0
    original_cape_length_z = -90.0
    top_x = original_top_x * scale_factor
    top_y_offset = original_top_y_offset * scale_factor
    bottom_x = original_bottom_x_spread * scale_factor
    bottom_y_offset = original_bottom_y_offset * scale_factor
    cape_length_z = original_cape_length_z * scale_factor

    glColor3f(0.0, 0.0, 0.545)
    glBegin(GL_QUADS)
    glVertex3f(-top_x, top_y_offset, 0)
    glVertex3f(top_x, top_y_offset, 0)
    glVertex3f(bottom_x, bottom_y_offset, cape_length_z)
    glVertex3f(-bottom_x, bottom_y_offset, cape_length_z)
    glEnd()
    glPopMatrix()

def drawPlayer():
    glPushMatrix()
    glTranslatef(playerPosition[0], playerPosition[1], playerPosition[2])
    glRotatef(playerAngle, 0, 0, 1)

    original_leg_separation_from_center = 12.0
    leg_separation = original_leg_separation_from_center * OVERALL_PLAYER_SCALE
    glPushMatrix(); glTranslatef(-leg_separation, 0, 0); drawLeg(LEG_LENGTH, silver_armor=True); glPopMatrix()
    glPushMatrix(); glTranslatef(leg_separation, 0, 0); drawLeg(LEG_LENGTH, silver_armor=True); glPopMatrix()

    glPushMatrix(); glTranslatef(0, 0, LEG_LENGTH); drawTorso(TORSO_LENGTH); glPopMatrix()

    original_head_radius = 25.0
    original_neck_gap_factor = 0.2
    head_radius_scaled = original_head_radius * OVERALL_PLAYER_SCALE
    neck_gap_scaled = head_radius_scaled * original_neck_gap_factor
    glPushMatrix(); glTranslatef(0, 0, LEG_LENGTH + TORSO_LENGTH + neck_gap_scaled); drawHead(head_radius_scaled, helmet=True); glPopMatrix()

    original_arm_x_offset_from_center = 30.0 * OVERALL_PLAYER_SCALE
    original_arm_z_offset_from_torso_top = -20.0 * OVERALL_PLAYER_SCALE
    arm_attach_z = LEG_LENGTH + TORSO_LENGTH + original_arm_z_offset_from_torso_top
    glPushMatrix(); glTranslatef(original_arm_x_offset_from_center, 0, arm_attach_z); glRotatef(45, 0, 1, 0); drawArm(ARM_LENGTH, silver_armor=True); glPopMatrix()
    glPushMatrix(); glTranslatef(-original_arm_x_offset_from_center, 0, arm_attach_z); glRotatef(-30, 0, 1, 0); drawArm(ARM_LENGTH, silver_armor=True); glPopMatrix()

    original_bow_local_x = original_arm_x_offset_from_center * 0.8
    original_bow_local_y = ARM_LENGTH * 0.3
    original_bow_local_z = arm_attach_z + ARM_LENGTH * 0.1
    glPushMatrix(); glTranslatef(original_bow_local_x, original_bow_local_y, original_bow_local_z); glRotatef(20, 0, 0, 1); glRotatef(70, 0, 1, 0); drawIndianBow(); glPopMatrix()

    original_armor_z_offset_from_leg_top = 20.0 * OVERALL_PLAYER_SCALE
    glPushMatrix(); glTranslatef(0, 0, LEG_LENGTH + original_armor_z_offset_from_leg_top); drawSilverArmor(); glPopMatrix()

    original_cape_z_offset_from_torso_top = -10.0 * OVERALL_PLAYER_SCALE
    glPushMatrix(); glTranslatef(0, 0, LEG_LENGTH + TORSO_LENGTH + original_cape_z_offset_from_torso_top); drawCape(); glPopMatrix()

    original_waist_z_offset_from_leg_top = -10.0 * OVERALL_PLAYER_SCALE
    glPushMatrix(); glTranslatef(0, 0, LEG_LENGTH + original_waist_z_offset_from_leg_top); drawWaistCloth(); glPopMatrix()

    glPopMatrix()

def drawELeg(length, silver_armor=False):
    glPushMatrix()
    if silver_armor: 
        glColor3f(0.6,0.6,0.7)
    else: 
        glColor3f(0.5, 0.3, 0.1)
    gluCylinder(gluNewQuadric(), 12, 10, length/2.0, 8, 3)
    glTranslatef(0, 0, length/2.0)
    if silver_armor: 
        glColor3f(0.5,0.5,0.6)
    gluCylinder(gluNewQuadric(), 10, 8, length/2.0, 8, 3)
    glTranslatef(0, 0, length/2.0)
    glColor3f(0.2, 0.1, 0.05)
    glutSolidCube(20)
    glPopMatrix()

def drawETorso(length):
    glPushMatrix()
    glColor3f(0.65, 0.65, 0.7)
    gluCylinder(gluNewQuadric(), 20, 18, length, 10, 3)
    glColor3f(0.5,0.5,0.6)
    glPushMatrix(); glTranslatef(18, 0, length * 0.7); glutSolidSphere(10, 8, 8); glPopMatrix()
    glPushMatrix(); glTranslatef(-18, 0, length * 0.7); glutSolidSphere(10, 8, 8); glPopMatrix()
    glPopMatrix()

def drawEHead(radius, helmet=False):
    glPushMatrix()
    if helmet:
        glColor3f(0.6, 0.6, 0.7)
        glutSolidSphere(radius, 12, 12)
        glPushMatrix(); glColor3f(0.7, 0.1, 0.1); glTranslatef(0, 0, radius * 0.8); gluCylinder(gluNewQuadric(), radius*0.2, 0, radius*1.2, 6, 2); glPopMatrix()
    else:
        glColor3f(0.7, 0.5, 0.3)
        glutSolidSphere(radius, 12, 12)
    glPopMatrix()

def drawEArm(length, silver_armor=False):
    glPushMatrix()
    if silver_armor: 
        glColor3f(0.6,0.6,0.7)
    else: 
        glColor3f(0.6, 0.4, 0.2)
    gluCylinder(gluNewQuadric(), 10, 8, length/2.0, 8, 3)
    glTranslatef(0, 0, length/2.0)
    if silver_armor: 
        glColor3f(0.55,0.55,0.65)
    gluCylinder(gluNewQuadric(), 8, 6, length/2.0, 8, 3)
    glTranslatef(0, 0, length/2.0)
    glColor3f(0.6, 0.4, 0.2)
    glutSolidSphere(7, 6, 6)
    glPopMatrix()

def drawEWaistCloth():
    glPushMatrix()
    glColor3f(0.8, 0.1, 0.1)
    gluCylinder(gluNewQuadric(), 25, 20, 30, 12, 3)
    glColor3f(0.6, 0.05, 0.05)
    glPushMatrix(); glTranslatef(0,0,5); gluDisk(gluNewQuadric(), 20, 22, 12,1); glPopMatrix()
    glPopMatrix()

def draw_single_enemy_model(position, angle):
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glRotatef(angle, 0, 0, 1)
    

    glPushMatrix(); glTranslatef(-12, 0, 0); drawELeg(ENEMY_LEG_LENGTH, silver_armor=True); glPopMatrix()
    glPushMatrix(); glTranslatef(12, 0, 0); drawELeg(ENEMY_LEG_LENGTH, silver_armor=True); glPopMatrix()
    glPushMatrix(); glTranslatef(0, 0, ENEMY_LEG_LENGTH); drawETorso(ENEMY_TORSO_LENGTH); glPopMatrix()
    glPushMatrix(); glTranslatef(0, 0, ENEMY_LEG_LENGTH + ENEMY_TORSO_LENGTH + 10); drawEHead(20, helmet=True); glPopMatrix()
    glPushMatrix(); glTranslatef(-25, 0, ENEMY_LEG_LENGTH + ENEMY_TORSO_LENGTH - 20); glRotatef(30, 0, 1, 0); drawEArm(ENEMY_ARM_LENGTH, silver_armor=True); glPopMatrix()
    glPushMatrix(); glTranslatef(25, 0, ENEMY_LEG_LENGTH + ENEMY_TORSO_LENGTH - 20); glRotatef(-30, 0, 1, 0); drawEArm(ENEMY_ARM_LENGTH, silver_armor=True); glPopMatrix()
    glPushMatrix(); glTranslatef(0, 0, ENEMY_LEG_LENGTH - 10); drawEWaistCloth(); glPopMatrix()

    glPopMatrix()

def draw_all_enemies():
    for enemy_data in enemyList:
        draw_single_enemy_model(enemy_data['pos'], enemy_data['angle'])

def drawArrow(x, y, z, direction_x, direction_y, direction_z):
    """Draws a long and thick arrow."""
    glPushMatrix()
    glTranslatef(x, y, z)

    magnitude = math.sqrt(direction_x**2 + direction_y**2 + direction_z**2)
    if magnitude > 0:
        axis_x = -direction_y
        axis_y = direction_x
        axis_z = 0

        dot_product = direction_z
        dot_product = max(-1.0, min(1.0, dot_product / magnitude))
        angle_rad = math.acos(dot_product)
        angle_deg = math.degrees(angle_rad)

        if abs(angle_deg) > 0.01 and (abs(axis_x) > 0.001 or abs(axis_y) > 0.001):
             glRotatef(angle_deg, axis_x, axis_y, axis_z)

    # Draw the arrow shaft
    glColor3f(0.6, 0.4, 0.2)
    gluCylinder(gluNewQuadric(), ARROW_SHAFT_RADIUS, ARROW_SHAFT_RADIUS, ARROW_SHAFT_LENGTH, 10, 10)

    # Draw the arrowhead
    glColor3f(0.8, 0.8, 0.9)
    glPushMatrix()
    glTranslatef(0, 0, ARROW_SHAFT_LENGTH)
    gluCylinder(gluNewQuadric(), ARROW_HEAD_RADIUS, 0, ARROW_HEAD_LENGTH, 10, 10)
    glPopMatrix()

    # Draw fletching
    glColor3f(0.9, 0.9, 0.9)
    fletching_start_z = ARROW_SHAFT_LENGTH * 0.8
    fletching_length = ARROW_SHAFT_LENGTH * 0.2
    fletching_width = ARROW_SHAFT_RADIUS * 2.5

    glPushMatrix()
    glTranslatef(0, 0, fletching_start_z)
    glBegin(GL_QUADS)
    glVertex3f(-fletching_width/2, 0, 0)
    glVertex3f(fletching_width/2, 0, 0)
    glVertex3f(fletching_width/2, 0, fletching_length)
    glVertex3f(-fletching_width/2, 0, fletching_length)

    glVertex3f(0, -fletching_width/2, 0)
    glVertex3f(0, fletching_width/2, 0)
    glVertex3f(0, fletching_width/2, fletching_length)
    glVertex3f(0, -fletching_width/2, fletching_length)
    glEnd()
    glPopMatrix()

    glPopMatrix()

def drawBrahmastraArrow(x, y, z, direction_x, direction_y, direction_z):
    """Draws a special orange Brahmastra arrow."""
    glPushMatrix()
    glTranslatef(x, y, z)

    magnitude = math.sqrt(direction_x**2 + direction_y**2 + direction_z**2)
    if magnitude > 0:
        axis_x = -direction_y
        axis_y = direction_x
        axis_z = 0

        dot_product = direction_z
        dot_product = max(-1.0, min(1.0, dot_product / magnitude))
        angle_rad = math.acos(dot_product)
        angle_deg = math.degrees(angle_rad)

        if abs(angle_deg) > 0.01 and (abs(axis_x) > 0.001 or abs(axis_y) > 0.001):
             glRotatef(angle_deg, axis_x, axis_y, axis_z)

    # Make the arrow bigger and orange
    arrow_scale = 3.0
    
    # Draw the arrow shaft (orange)
    glColor3f(1.0, 0.5, 0.0)  # Orange
    gluCylinder(gluNewQuadric(), ARROW_SHAFT_RADIUS * arrow_scale, 
                ARROW_SHAFT_RADIUS * arrow_scale, 
                ARROW_SHAFT_LENGTH * arrow_scale, 12, 12)

    # Draw the arrowhead (bright orange)
    glColor3f(1.0, 0.7, 0.0)  # Brighter orange
    glPushMatrix()
    glTranslatef(0, 0, ARROW_SHAFT_LENGTH * arrow_scale)
    gluCylinder(gluNewQuadric(), ARROW_HEAD_RADIUS * arrow_scale, 0, 
                ARROW_HEAD_LENGTH * arrow_scale, 12, 12)
    glPopMatrix()

    # Draw fletching (golden)
    glColor3f(1.0, 0.84, 0.0)  # Gold
    fletching_start_z = (ARROW_SHAFT_LENGTH * arrow_scale) * 0.8
    fletching_length = (ARROW_SHAFT_LENGTH * arrow_scale) * 0.2
    fletching_width = (ARROW_SHAFT_RADIUS * arrow_scale) * 3.0

    glPushMatrix()
    glTranslatef(0, 0, fletching_start_z)
    glBegin(GL_QUADS)
    glVertex3f(-fletching_width/2, 0, 0)
    glVertex3f(fletching_width/2, 0, 0)
    glVertex3f(fletching_width/2, 0, fletching_length)
    glVertex3f(-fletching_width/2, 0, fletching_length)

    glVertex3f(0, -fletching_width/2, 0)
    glVertex3f(0, fletching_width/2, 0)
    glVertex3f(0, fletching_width/2, fletching_length)
    glVertex3f(0, -fletching_width/2, fletching_length)
    glEnd()
    glPopMatrix()

    # Add a glowing effect (concentric spheres)
    glColor3f(1.0, 0.5, 0.0)  # Orange 
    glPushMatrix()
    glTranslatef(0, 0, ARROW_SHAFT_LENGTH * arrow_scale * 0.5)
    glutSolidSphere((ARROW_SHAFT_RADIUS + ARROW_HEAD_RADIUS) * arrow_scale * 0.8, 16, 16)
    glPopMatrix()

    glPopMatrix()


def drawMayastraArrow(x, y, z, direction_x, direction_y, direction_z):
    """Draws a special blue Mayastra arrow with golden head."""
    glPushMatrix()
    glTranslatef(x, y, z)

    magnitude = math.sqrt(direction_x**2 + direction_y**2 + direction_z**2)
    if magnitude > 0:
        axis_x = -direction_y
        axis_y = direction_x
        axis_z = 0

        dot_product = direction_z
        dot_product = max(-1.0, min(1.0, dot_product / magnitude))
        angle_rad = math.acos(dot_product)
        angle_deg = math.degrees(angle_rad)

        if abs(angle_deg) > 0.01 and (abs(axis_x) > 0.001 or abs(axis_y) > 0.001):
             glRotatef(angle_deg, axis_x, axis_y, axis_z)

    # Make the arrow bigger and blue
    arrow_scale = 3.0
    
    # Draw the arrow shaft (blue)
    glColor3f(0.0, 0.5, 1.0)  # Blue
    gluCylinder(gluNewQuadric(), ARROW_SHAFT_RADIUS * arrow_scale, 
                ARROW_SHAFT_RADIUS * arrow_scale, 
                ARROW_SHAFT_LENGTH * arrow_scale, 12, 12)

    # Draw the arrowhead (golden)
    glColor3f(1.0, 0.84, 0.0)  # Gold
    glPushMatrix()
    glTranslatef(0, 0, ARROW_SHAFT_LENGTH * arrow_scale)
    gluCylinder(gluNewQuadric(), ARROW_HEAD_RADIUS * arrow_scale, 0, 
                ARROW_HEAD_LENGTH * arrow_scale, 12, 12)
    glPopMatrix()

    # Draw fletching (light blue)
    glColor3f(0.5, 0.8, 1.0)  # Light blue
    fletching_start_z = (ARROW_SHAFT_LENGTH * arrow_scale) * 0.8
    fletching_length = (ARROW_SHAFT_LENGTH * arrow_scale) * 0.2
    fletching_width = (ARROW_SHAFT_RADIUS * arrow_scale) * 3.0

    glPushMatrix()
    glTranslatef(0, 0, fletching_start_z)
    glBegin(GL_QUADS)
    glVertex3f(-fletching_width/2, 0, 0)
    glVertex3f(fletching_width/2, 0, 0)
    glVertex3f(fletching_width/2, 0, fletching_length)
    glVertex3f(-fletching_width/2, 0, fletching_length)

    glVertex3f(0, -fletching_width/2, 0)
    glVertex3f(0, fletching_width/2, 0)
    glVertex3f(0, fletching_width/2, fletching_length)
    glVertex3f(0, -fletching_width/2, fletching_length)
    glEnd()
    glPopMatrix()

    # Add a glowing effect (concentric spheres)
    glColor3f(0.0, 0.5, 1.0)  # Blue 
    glPushMatrix()
    glTranslatef(0, 0, ARROW_SHAFT_LENGTH * arrow_scale * 0.5)
    glutSolidSphere((ARROW_SHAFT_RADIUS + ARROW_HEAD_RADIUS) * arrow_scale * 0.8, 16, 16)
    glPopMatrix()

    glPopMatrix()


def moveEnemies():
    global playerLife, modeOver, enemyList 
    if modeOver: return
    player_effective_radius = PLAYER_HEIGHT * 0.2
    enemy_effective_radius = (ENEMY_LEG_LENGTH + ENEMY_TORSO_LENGTH) * ENEMY_OVERALL_SCALE * 0.2

    for i, enemy_data in enumerate(enemyList):
        enemy_pos = enemy_data['pos']
        dx = playerPosition[0] - enemy_pos[0]
        dy = playerPosition[1] - enemy_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        collision_threshold = player_effective_radius + enemy_effective_radius

        if distance < collision_threshold and mayastra_state != "active":  # Only hurt player if Mayastra not active
            if not modeOver:
                playerLife -= 5
                if playerLife <= 1250:
                    playerLife = 1250
                    modeOver = True
                    print("Game Over! - Touched by enemy")
        else:
            angle_rad = math.atan2(dy, dx)
            enemy_data['angle'] = (math.degrees(angle_rad) - 90 + 360) % 360
            enemy_pos[0] += enemySpeed * math.cos(angle_rad)
            enemy_pos[1] += enemySpeed * math.sin(angle_rad)

    arrows_to_remove_indices = []
    for i, arrow_data in enumerate(Arrows):
        arrow_pos = arrow_data['pos']
        # Skip collision check with player if Mayastra is active and arrow is redirected
        if SHIELD_ACTIVE:
            shield_radius = PLAYER_HEIGHT * 0.7
            dx = arrow_pos[0] - playerPosition[0]
            dy = arrow_pos[1] - playerPosition[1]
            dz = arrow_pos[2] - (PLAYER_HEIGHT * 0.5)  # Center of shield
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if distance < shield_radius:
                arrows_to_remove_indices.append(i)
                continue 
            
        if mayastra_state == "active" and arrow_data.get('mayastra_redirected', False):
            continue
            
        player_collision_z_min = PLAYER_HEIGHT * 0.1
        player_collision_z_max = PLAYER_HEIGHT * 0.9
        dx_arrow_player = arrow_pos[0] - playerPosition[0]
        dy_arrow_player = arrow_pos[1] - playerPosition[1]
        dist_sq_xy_arrow_player = dx_arrow_player**2 + dy_arrow_player**2

        if dist_sq_xy_arrow_player < (player_effective_radius + ARROW_HEAD_RADIUS)**2:
            if player_collision_z_min < arrow_pos[2] < player_collision_z_max:
                if not modeOver:
                    playerLife -= ARROW_DAMAGE
                    if playerLife <= 1250:
                        playerLife = 1250
                        modeOver = True
                        print("Game Over! - Shot by enemy arrow")
                arrows_to_remove_indices.append(i)
    
    for index in sorted(arrows_to_remove_indices, reverse=True):
        if index < len(Arrows):
            del Arrows[index]
    if modeOver:
        Arrows.clear()




def enemyShoot():
    global Arrows
    if modeOver or brahmastra_state == "firing":
        return  # Don't shoot during game over or Brahmastra effect
    
    for enemy_data in enemyList:
        enemy_data['shoot_timer_frames'] += 1
        player_center_z = playerPosition[2] + PLAYER_HEIGHT / 2
        enemy_arrow_spawn_z = enemy_data['pos'][2] + (ENEMY_LEG_LENGTH + ENEMY_TORSO_LENGTH*0.7) * ENEMY_OVERALL_SCALE
        dx = playerPosition[0] - enemy_data['pos'][0]
        dy = playerPosition[1] - enemy_data['pos'][1]
        dz = player_center_z - enemy_arrow_spawn_z
        distance_to_player = math.sqrt(dx**2 + dy**2 + dz**2)
        current_shoot_interval = enemy_data.get('current_shoot_interval_frames',
                                            random.randint(ENEMY_MIN_SHOOT_INTERVAL_FRAMES, ENEMY_MAX_SHOOT_INTERVAL_FRAMES))
        enemy_data['current_shoot_interval_frames'] = current_shoot_interval

        if distance_to_player < ENEMY_SHOOT_RANGE and enemy_data['shoot_timer_frames'] >= current_shoot_interval:
            if distance_to_player > 0:
                dir_x, dir_y, dir_z = dx / distance_to_player, dy / distance_to_player, dz / distance_to_player
            else:
                dir_x, dir_y, dir_z = 0, 1, 0
            spawn_offset_dist = (ARROW_SHAFT_LENGTH + ARROW_HEAD_LENGTH) * 0.5
            arrow_origin_x = enemy_data['pos'][0] + dir_x * spawn_offset_dist
            arrow_origin_y = enemy_data['pos'][1] + dir_y * spawn_offset_dist
            arrow_origin_z = enemy_arrow_spawn_z
            Arrows.append({
                'pos': [arrow_origin_x, arrow_origin_y, arrow_origin_z],
                'direction': [dir_x, dir_y, dir_z],
                'is_player_arrow': False,
                'mayastra_redirected': mayastra_state == "active"  # Set to True if Mayastra is active
            })
            enemy_data['shoot_timer_frames'] = 0
            enemy_data['current_shoot_interval_frames'] = random.randint(ENEMY_MIN_SHOOT_INTERVAL_FRAMES, ENEMY_MAX_SHOOT_INTERVAL_FRAMES)


def updateEnemyShootTimers(delta_time):
    global enemyList, Arrows, playerPosition
    for enemy in enemyList:
        enemy['shoot_timer_frames'] -= 1
        if enemy['shoot_timer_frames'] <= 0:
            # Calculate arrow direction
            enemy_pos_x, enemy_pos_y, enemy_pos_z = enemy['pos']
            player_pos_x, player_pos_y, player_pos_z = playerPosition
            dx = player_pos_x - enemy_pos_x
            dy = player_pos_y - enemy_pos_y
            dz = player_pos_z - enemy_pos_z
            
            # Normalize the direction vector
            magnitude = math.sqrt(dx * dx + dy * dy + dz * dz)
            if magnitude > 0:
                dx /= magnitude
                dy /= magnitude
                dz /= magnitude
            
            new_arrow = {
                'pos': [enemy_pos_x, enemy_pos_y, enemy_pos_z + ENEMY_TORSO_LENGTH * 0.8],
                'direction': [dx, dy, dz],
                'is_enemy_arrow': True,
                'is_mayastra': False
            }
            Arrows.append(new_arrow)
            enemy['shoot_timer_frames'] = random.randint(ENEMY_MIN_SHOOT_INTERVAL_FRAMES, ENEMY_MAX_SHOOT_INTERVAL_FRAMES)

def updateArrowPositions(delta_time):
    global Arrows, enemyList, playerPosition, playerLife, playerScore, mayastra_state
    
    arrows_to_remove = []
    
    for i, arrow in enumerate(Arrows):
        arrow['pos'][0] += arrow['direction'][0] * ARROW_SPEED
        arrow['pos'][1] += arrow['direction'][1] * ARROW_SPEED
        arrow['pos'][2] += arrow['direction'][2] * ARROW_SPEED
        
        
        if not arrow.get('is_enemy_arrow', False):  # Player's arrow
            
            closest_enemy_index = -1
            min_distance = float('inf')
            
            for j, enemy in enumerate(enemyList):
                enemy_pos_x, enemy_pos_y, enemy_pos_z = enemy['pos']
                
                # Cylinder-sphere collision approximation
                dist_to_arrow_tip = math.sqrt(
                    (arrow['pos'][0] - enemy_pos_x)**2 +
                    (arrow['pos'][1] - enemy_pos_y)**2 +
                    (arrow['pos'][2] - enemy_pos_z)**2
                )
                
                dist_to_arrow_base = math.sqrt(
                    (arrow['pos'][0] - arrow['direction'][0] * ARROW_SHAFT_LENGTH - enemy_pos_x)**2 +
                    (arrow['pos'][1] - arrow['direction'][1] * ARROW_SHAFT_LENGTH - enemy_pos_y)**2 +
                    (arrow['pos'][2] - arrow['direction'][2] * ARROW_SHAFT_LENGTH - enemy_pos_z)**2
                )
                
                if (dist_to_arrow_tip < 20) or (dist_to_arrow_base < 20):
                    if mayastra_state != "active":
                        playerScore += 1
                        arrows_to_remove.append(i)
                        del enemyList[j]
                        break
                    
                
        else: # Enemy arrow
            player_pos_x, player_pos_y, player_pos_z = playerPosition
            dist_to_player = math.sqrt(
                (arrow['pos'][0] - player_pos_x)**2 +
                (arrow['pos'][1] - player_pos_y)**2 +
                (arrow['pos'][2] - player_pos_z)**2
            )
            if dist_to_player < 30:
                playerLife -= ARROW_DAMAGE
                arrows_to_remove.append(i)
                if playerLife <= 1250:
                    modeOver = True
                    return
                

        # Remove arrows that go out of bounds
        if (arrow['pos'][0] > BATTLEFIELD_BOUNDS or arrow['pos'][0] < -BATTLEFIELD_BOUNDS or
            arrow['pos'][1] > BATTLEFIELD_BOUNDS or arrow['pos'][1] < -BATTLEFIELD_BOUNDS or
            arrow['pos'][2] > 2000 or arrow['pos'][2] < -2000):
            arrows_to_remove.append(i)

    # Remove the arrows outside the loop
    arrows_to_remove.reverse()
    for index in arrows_to_remove:
        if index < len(Arrows):
            del Arrows[index]


def updateBrahmastra(delta_time):
    global brahmastra_state, brahmastra_arrow, brahmastra_last_used_time
    global enemyList, Arrows, playerScore  # Add playerScore to globals
    
    current_time = time.time()
    
    # Check cooldown status
    if brahmastra_state == "cooldown" and (current_time - brahmastra_last_used_time) >= BRAHMASTRA_COOLDOWN:
        brahmastra_state = "ready"
    
    # Update the Brahmastra arrow if it's firing
    if brahmastra_state == "firing" and brahmastra_arrow is None:
        # Add score for each enemy killed (10 points per enemy)
        enemies_killed = len(enemyList)
        playerScore += enemies_killed * 1
        
        # Kill all enemies immediately
        enemyList.clear()
        Arrows.clear()  # Clear all other arrows too
        
        # Start cooldown
        brahmastra_state = "cooldown"
        brahmastra_last_used_time = current_time

def updateMayastra(delta_time):
    global mayastra_state, mayastra_arrow, mayastra_last_used_time, mayastra_active_until
    global enemyList, Arrows
    
    current_time = time.time()
    
    # Check cooldown status
    if mayastra_state == "cooldown" and (current_time - mayastra_last_used_time) >= MAYASTRA_COOLDOWN:
        mayastra_state = "ready"
    
    # Update the Mayastra arrow if it's firing
    if mayastra_state == "firing" and mayastra_arrow:
        mayastra_arrow['pos'][2] += ARROW_SPEED * 1.5
        if mayastra_arrow['pos'][2] > BATTLEFIELD_SIZE * 0.7:
            mayastra_arrow = None
            mayastra_state = "active"
            mayastra_active_until = current_time + MAYASTRA_DURATION
            
            # Tag all existing enemy arrows for redirection
            for arrow in Arrows:
                if not arrow.get('is_player_arrow', False):
                    arrow['mayastra_redirected'] = True
                    arrow['original_direction'] = arrow['direction'].copy()
                    arrow['redirect_start_time'] = current_time
                    # Initialize target_enemy_index to -1 (no target)
                    arrow['target_enemy_index'] = -1
    
    # If Mayastra is active, update the redirected arrows
    if mayastra_state == "active":
        # Check if the active duration has expired
        if current_time > mayastra_active_until:
            mayastra_state = "cooldown"
            mayastra_last_used_time = current_time
            # Remove all redirected flags
            for arrow in Arrows:
                if 'mayastra_redirected' in arrow:
                    del arrow['mayastra_redirected']
                    if 'target_enemy_index' in arrow:
                        del arrow['target_enemy_index']
        else:
            # Update each redirected arrow's direction
            for arrow in Arrows:
                if arrow.get('mayastra_redirected', False):
                    # Make sure target_enemy_index exists
                    if 'target_enemy_index' not in arrow:
                        arrow['target_enemy_index'] = -1
                    
                    # If we don't have a target or the target is dead, find a new one
                    if arrow['target_enemy_index'] == -1 or arrow['target_enemy_index'] >= len(enemyList):
                        if enemyList:  # Only redirect if there are enemies
                            arrow['target_enemy_index'] = random.randint(0, len(enemyList)-1)
                    
                    # If we have a valid target, calculate direction to it
                    if arrow['target_enemy_index'] != -1 and arrow['target_enemy_index'] < len(enemyList):
                        target_enemy = enemyList[arrow['target_enemy_index']]
                        target_pos = target_enemy['pos']
                        
                        # Calculate direction vector to target
                        dx = target_pos[0] - arrow['pos'][0]
                        dy = target_pos[1] - arrow['pos'][1]
                        dz = (target_pos[2] + (ENEMY_LEG_LENGTH + ENEMY_TORSO_LENGTH/2) * ENEMY_OVERALL_SCALE) - arrow['pos'][2]
                        
                        # Normalize the direction vector
                        length = math.sqrt(dx*dx + dy*dy + dz*dz)
                        if length > 0:
                            arrow['direction'] = [dx/length, dy/length, dz/length]

def moveArrows():
    global Arrows, brahmastra_arrow, mayastra_arrow, enemyList, playerScore
    arrows_to_remove_indices = []
    half_b_world = BATTLEFIELD_BOUNDS * 1.5
    
    # Check for arrow collisions with enemies
    for i, arrow_data in enumerate(Arrows):
        arrow_pos = arrow_data['pos']
        direction = arrow_data['direction']
        
        # Move the arrow
        arrow_pos[0] += direction[0] * ARROW_SPEED
        arrow_pos[1] += direction[1] * ARROW_SPEED
        arrow_pos[2] += direction[2] * ARROW_SPEED
        
        # Check if arrow is out of bounds
        if not (-half_b_world < arrow_pos[0] < half_b_world and \
                -half_b_world < arrow_pos[1] < half_b_world and \
                0 < arrow_pos[2] < BATTLEFIELD_SIZE * 0.7):
            arrows_to_remove_indices.append(i)
            continue
        
        # Check for collisions with enemies if this is a redirected arrow
        if arrow_data.get('mayastra_redirected', False):
            # Check collision with each enemy
            for j, enemy_data in enumerate(enemyList):
                enemy_pos = enemy_data['pos']
                enemy_z = enemy_pos[2] + (ENEMY_LEG_LENGTH + ENEMY_TORSO_LENGTH/2) * ENEMY_OVERALL_SCALE
                dx = arrow_pos[0] - enemy_pos[0]
                dy = arrow_pos[1] - enemy_pos[1]
                dz = arrow_pos[2] - enemy_z
                
                # Calculate distance squared
                dist_sq = dx*dx + dy*dy + dz*dz
                collision_radius = (ENEMY_TORSO_LENGTH * ENEMY_OVERALL_SCALE * 0.5) ** 2
                
                # If collision detected
                if dist_sq < collision_radius:
                    # Remove the enemy
                    enemyList.pop(j)
                    # Remove the arrow
                    arrows_to_remove_indices.append(i)
                    # Increment score (20 points for Mayastra kills)
                    playerScore += 1
                    break
    
    # Move Brahmastra arrow if it exists
    if brahmastra_arrow:
        brahmastra_arrow['pos'][2] += ARROW_SPEED * 1.5
        if brahmastra_arrow['pos'][2] > BATTLEFIELD_SIZE * 0.7:
            brahmastra_arrow = None
    
    # Move Mayastra arrow if it exists
    if mayastra_arrow:
        mayastra_arrow['pos'][2] += ARROW_SPEED * 1.5
        if mayastra_arrow['pos'][2] > BATTLEFIELD_SIZE * 0.7:
            mayastra_arrow = None
    
    # Remove arrows that are out of bounds or collided with enemies
    for index in sorted(arrows_to_remove_indices, reverse=True):
        if index < len(Arrows):
            del Arrows[index]


# --- AgniAstra Drawing Function --- 

def drawAgniAstra(x, y, z, radius, current_age_frames):
    glPushMatrix()
    glTranslatef(x, y, z)
    # Pulsating effect for size and color
    pulse_factor = 1.0 + 0.2 * math.sin(current_age_frames * 0.2) # Slow pulse
    current_radius = radius * pulse_factor
    
    # Base color orangish-red, pulsating towards yellow
    r, g, b = AgniAstra_COLOR
    g_pulse = min(1.0, g + 0.3 * (0.5 + 0.5 * math.sin(current_age_frames * 0.25))) # Pulse green towards yellow
    glColor3f(r, g_pulse, b * (0.8 + 0.2*pulse_factor) ) # Slightly dim blue for depth
    
    glutSolidSphere(current_radius, 16, 12) # Fewer slices/stacks for performance
    glPopMatrix()

# --- AgniAstra Logic --- 

def useAgniAstra():
    global AgniAstra_last_use_frame, activeAgniAstras, current_frame_count
    if current_frame_count - AgniAstra_last_use_frame >= AgniAstra_COOLDOWN_FRAMES:
        # Target a random location on the battlefield (on the ground Z=0)
        # Ensure it's within bounds, away from edges
        target_x = random.uniform(-BATTLEFIELD_BOUNDS + AgniAstra_target_margin, BATTLEFIELD_BOUNDS - AgniAstra_target_margin)
        target_y = random.uniform(-BATTLEFIELD_BOUNDS + AgniAstra_target_margin, BATTLEFIELD_BOUNDS - AgniAstra_target_margin)
        target_z = AgniAstra_RADIUS * 0.5 # AgniAstra center slightly above ground for better visual

        activeAgniAstras.append({
            'pos': [target_x, target_y, target_z],
            'radius': AgniAstra_RADIUS,
            'age_frames': 0,
            'duration_frames': AgniAstra_DURATION_FRAMES
        })
        AgniAstra_last_use_frame = current_frame_count
        print(f"AgniAstra cast at [{target_x:.1f}, {target_y:.1f}]!")
    else:
        remaining_cooldown = (AgniAstra_COOLDOWN_FRAMES - (current_frame_count - AgniAstra_last_use_frame)) / 60.0 # Approx seconds
        print(f"AgniAstra on cooldown for {remaining_cooldown:.1f}s")


def updateAndProcessAgniAstras():
    global activeAgniAstras, enemyList, enemiesKilledByAgniAstra, playerScore
    AgniAstras_to_remove_indices = []
    enemies_to_remove_indices = [] # Store indices of enemies hit by any AgniAstra this frame

    for i, AgniAstra in enumerate(activeAgniAstras):
        AgniAstra['age_frames'] += 1
        if AgniAstra['age_frames'] == 1: # On the first frame of activation, check for hits
            fb_pos = AgniAstra['pos']
            fb_radius_sq = AgniAstra['radius']**2
            
            current_enemies_hit_by_this_AgniAstra = 0
        
            # collect indices of enemies to remove
            
            temp_enemy_indices_hit_this_AgniAstra = []
            for j, enemy_data in enumerate(enemyList):
                if j in enemies_to_remove_indices : 
                    continue # Already marked for removal by another AgniAstra

                enemy_pos = enemy_data['pos']
                # Check 2D distance first (AgniAstra AoE is circular on ground)
                dx = enemy_pos[0] - fb_pos[0]
                dy = enemy_pos[1] - fb_pos[1]
                dist_sq_to_enemy = dx**2 + dy**2

                # Enemy effective radius for collision with AgniAstra's edge
                enemy_body_radius = ENEMY_TORSO_LENGTH * ENEMY_OVERALL_SCALE * 0.5 # Approximation
                
                if dist_sq_to_enemy < (AgniAstra['radius'] + enemy_body_radius)**2 : # Check if enemy center is within AoE
                    temp_enemy_indices_hit_this_AgniAstra.append(j)
                    current_enemies_hit_by_this_AgniAstra +=1
            
            if temp_enemy_indices_hit_this_AgniAstra:
                enemiesKilledByAgniAstra += current_enemies_hit_by_this_AgniAstra
                playerScore += current_enemies_hit_by_this_AgniAstra * 1 # Score for AgniAstra kills
                print(f"AgniAstra hit {current_enemies_hit_by_this_AgniAstra} enemies! Total AgniAstra kills: {enemiesKilledByAgniAstra}")
                # Add to master list of enemies to remove this frame
                for idx in temp_enemy_indices_hit_this_AgniAstra:
                    if idx not in enemies_to_remove_indices:
                        enemies_to_remove_indices.append(idx)


        if AgniAstra['age_frames'] >= AgniAstra['duration_frames']:
            AgniAstras_to_remove_indices.append(i)

    # Remove expired AgniAstras
    for index in sorted(AgniAstras_to_remove_indices, reverse=True):
        if index < len(activeAgniAstras):
            del activeAgniAstras[index]
            
    # Remove enemies hit by AgniAstras
    if enemies_to_remove_indices:
        # Sort indices in reverse to avoid issues when deleting from list
        for index in sorted(list(set(enemies_to_remove_indices)), reverse=True): # Use set to ensure unique indices
            if index < len(enemyList):
                del enemyList[index]


# --- VajraAstra Logic --- 

def create_jagged_line_segments(start_pos, end_pos, num_segments, max_offset_xy, max_offset_z_deviation):
    segments = []
    current_pos = list(start_pos)
    direction_vector = [e - s for s, e in zip(start_pos, end_pos)]
    total_distance = math.sqrt(sum(d*d for d in direction_vector))
    if total_distance < 1.0: return [{'start': tuple(start_pos), 'end': tuple(end_pos)}]
    unit_direction = [d / total_distance for d in direction_vector]
    ideal_segment_length = total_distance / num_segments
    for i in range(num_segments):
        ideal_next_pos_segment_end = [c + ud * ideal_segment_length for c, ud in zip(current_pos, unit_direction)]
        if i < num_segments - 1:
            offset_x, offset_y, offset_z = random.uniform(-max_offset_xy, max_offset_xy), random.uniform(-max_offset_xy, max_offset_xy), random.uniform(-max_offset_z_deviation, max_offset_z_deviation)
            actual_next_pos = [ideal_next_pos_segment_end[0] + offset_x, ideal_next_pos_segment_end[1] + offset_y, ideal_next_pos_segment_end[2] + offset_z]
        else: actual_next_pos = list(end_pos)
        segments.append({'start': tuple(current_pos), 'end': tuple(actual_next_pos)}); current_pos = actual_next_pos
    return segments

def generate_VajraAstra_visual_structure(target_enemy_center_pos):
    bolt_visual_parts = []
    sky_origin_z = BATTLEFIELD_SIZE * 0.6
    main_trunk_start_pos = (target_enemy_center_pos[0] + random.uniform(-150, 150), target_enemy_center_pos[1] + random.uniform(-150, 150), sky_origin_z)
    main_trunk_segments = create_jagged_line_segments(main_trunk_start_pos, target_enemy_center_pos, random.randint(7, 12), 100, 70)
    bolt_visual_parts.append({'segments': main_trunk_segments, 'color': (0.2, 0.2, 1.0), 'width': 3.0})
    num_branches = random.randint(5, 10)
    if main_trunk_segments:
        for _ in range(num_branches):
            branch_origin_segment_choice = random.choice(main_trunk_segments)
            branch_start_pos = branch_origin_segment_choice['start']
            base_branch_length = (sky_origin_z - target_enemy_center_pos[2]) * random.uniform(0.3, 0.7)
            branch_length = max(80, base_branch_length * (branch_start_pos[2] / sky_origin_z if sky_origin_z > 0 else 1.0))
            angle_xy = random.uniform(0, 2 * math.pi)
            branch_end_x, branch_end_y = branch_start_pos[0] + math.cos(angle_xy) * branch_length * random.uniform(0.4, 0.8), branch_start_pos[1] + math.sin(angle_xy) * branch_length * random.uniform(0.4, 0.8)
            branch_end_z = max(0, branch_start_pos[2] - branch_length * random.uniform(0.5, 1.5))
            branch_line_segments = create_jagged_line_segments(branch_start_pos, (branch_end_x, branch_end_y, branch_end_z), random.randint(4, 7), 60, 40)
            bolt_visual_parts.append({'segments': branch_line_segments, 'color': (1.0, 1.0, 1.0), 'width': 1.5})
    return bolt_visual_parts

def trigger_VajraAstra_attack():
    global active_VajraAstras, enemyList, playerScore, modeOver, last_VajraAstra_kill_count, VajraAstra_cooldown_remaining_frames
    if modeOver or VajraAstra_cooldown_remaining_frames > 0: return
    VajraAstra_cooldown_remaining_frames = VajraAstra_COOLDOWN_FRAMES
    if not enemyList: last_VajraAstra_kill_count = 0; print("VajraAstra: No enemies. Cooldown started."); return
    num_potential_strikes = min(VajraAstra_STRIKES_COUNT, len(enemyList))
    indices_of_enemies_to_strike = sorted(random.sample(range(len(enemyList)), num_potential_strikes), reverse=True)
    kills_this_strike = 0
    for index in indices_of_enemies_to_strike:
        if index < len(enemyList):
            enemy_data = enemyList[index]
            enemy_model_height = (ENEMY_LEG_LENGTH + ENEMY_TORSO_LENGTH + 20) * ENEMY_OVERALL_SCALE
            target_pos = (enemy_data['pos'][0], enemy_data['pos'][1], enemy_data['pos'][2] + enemy_model_height / 2.0)
            active_VajraAstras.append({'visuals': generate_VajraAstra_visual_structure(target_pos), 'timer': VajraAstra_DURATION_FRAMES})
            del enemyList[index]; playerScore += 1; kills_this_strike += 1
    last_VajraAstra_kill_count = kills_this_strike
    print(f"VajraAstra: Kills: {kills_this_strike}. Cooldown active." if kills_this_strike > 0 else "VajraAstra: No hits. Cooldown active.")

def update_active_VajraAstras():
    global active_VajraAstras
    active_VajraAstras = [bolt for bolt in active_VajraAstras if (bolt.update({'timer': bolt['timer'] - 1}) or bolt['timer'] > 0)]

def draw_all_active_VajraAstras():
    if not active_VajraAstras: return
    for bolt_effect in active_VajraAstras:
        for part in bolt_effect['visuals']:
            glColor3f(*part['color']); glLineWidth(part['width'])
            glBegin(GL_LINES)
            for segment in part['segments']: glVertex3f(*segment['start']); glVertex3f(*segment['end'])
            glEnd()
    glLineWidth(1.0)



'''LISTENERS'''

def keyboardListener(key, x_m, y_m):
    global playerAngle, playerPosition, modeOver, playerLife, playerScore, is_day, camera_pos_list
    global brahmastra_state, brahmastra_arrow, brahmastra_last_used_time  # Declare the variable as global
    global mayastra_state, mayastra_arrow, mayastra_last_used_time
    global enemyList, Arrows, active_VajraAstras, VajraAstra_cooldown_remaining_frames, last_VajraAstra_kill_count
    global AgniAstra_last_use_frame, current_frame_count 
    global SHIELD_ACTIVE, SHIELD_TIME, shield_cooldown_timer

    if key.lower() == b't':
        is_day = not is_day
        return
    
    # AgniAstra action
    if not modeOver and key.lower() == b'f':
        useAgniAstra()
        return # Consume 'f' key press
    
    # VajraAstra action 
    if not modeOver and key.lower() == b'v': 
        trigger_VajraAstra_attack() 
        return # Consume 'v' key press
    
    
    if key.lower() == b'p' and not modeOver:  #  for Pawan Astra activation
        activate_pawan_astra()
    if key.lower() == b'h' and not modeOver:  # Activate shield with 'h' key
        activate_shield()
    
    # Add Mayastra activation with 'M' key
    if key.lower() == b'm' and not modeOver:
        if mayastra_state == "ready":
            print("Mayastra activated!")
            mayastra_state = "firing"
            # Create the Mayastra arrow at player position
            arrow_origin_x = playerPosition[0]
            arrow_origin_y = playerPosition[1]
            arrow_origin_z = playerPosition[2] + PLAYER_HEIGHT * 0.7  # Spawn above player's head
            
            # Point straight up
            mayastra_arrow = {
                'pos': [arrow_origin_x, arrow_origin_y, arrow_origin_z],
                'direction': [0, 0, 1],  # Pointing upward
                'is_mayastra': True
            }
        elif mayastra_state == "cooldown":
            cooldown_remaining = MAYASTRA_COOLDOWN - (time.time() - mayastra_last_used_time)
            print(f"Mayastra on cooldown! {cooldown_remaining:.1f}s remaining")
        return
    
    # Brahmastra activation with 'B' key
    if key.lower() == b'b' and not modeOver:
        if brahmastra_state == "ready":
            print("Brahmastra activated!")
            brahmastra_state = "firing"
            # Create the Brahmastra arrow at player position
            arrow_origin_x = playerPosition[0]
            arrow_origin_y = playerPosition[1]
            arrow_origin_z = playerPosition[2] + PLAYER_HEIGHT * 0.7  # Spawn above player's head
            
            # Point straight up
            brahmastra_arrow = {
                'pos': [arrow_origin_x, arrow_origin_y, arrow_origin_z],
                'direction': [0, 0, 1],  # Pointing upward
                'is_brahmastra': True
            }
        elif brahmastra_state == "cooldown":
            cooldown_remaining = BRAHMASTRA_COOLDOWN - (time.time() - brahmastra_last_used_time)
            print(f"Brahmastra on cooldown! {cooldown_remaining:.1f}s remaining")
        return

    # Original keyboard controls below
    px, py, pz = playerPosition
    if not modeOver:
        if key == b's':
            px_change = playerSpeed * math.sin(math.radians(playerAngle))
            py_change = playerSpeed * math.cos(math.radians(playerAngle))
            px += px_change; py += py_change
        elif key == b'w':
            px_change = playerSpeed * math.sin(math.radians(playerAngle))
            py_change = playerSpeed * math.cos(math.radians(playerAngle))
            px -= px_change; py -= py_change
        elif key == b'a': playerAngle = (playerAngle + playerTurnSpeed) % 360
        elif key == b'd': playerAngle = (playerAngle - playerTurnSpeed + 360) % 360
        
        half_b_player = BATTLEFIELD_BOUNDS - (PLAYER_HEIGHT*0.15)
        px = max(-half_b_player, min(px, half_b_player))
        py = max(-half_b_player, min(py, half_b_player))
        playerPosition = [px, py, pz]

    if key == b'r':
        print("Restarting game")
        modeOver = False
        camera_pos_list = [0, 2000, 2000]
        playerPosition = [0, 0, 0]; playerAngle = 0
        playerLife = 5000; playerScore = 0
        enemyList.clear(); Arrows.clear() 
        activeAgniAstras.clear(); active_VajraAstras.clear() 
        global enemiesKilledByAgniAstra # Reset this counter
        enemiesKilledByAgniAstra = 0
        AgniAstra_last_use_frame = -AgniAstra_COOLDOWN_FRAMES # Reset AgniAstra cooldown
        VajraAstra_cooldown_remaining_frames=0; last_VajraAstra_kill_count=0 # Reset VajraAstra cooldown and kill count

        # Reset special weapons states 
        SHIELD_ACTIVE = False
        SHIELD_TIME = 0
        shield_cooldown_timer = 0
        brahmastra_state = "ready"
        brahmastra_arrow = None
        brahmastra_last_used_time = 0
        mayastra_state = "ready"
        mayastra_arrow = None
        mayastra_last_used_time = 0
        last_spawn_time = time.time()  # Reset spawn timer on restart


def specialKeyListener(key, cam_x, cam_y):
    global camera_pos_list
    move_speed, zoom_speed = 100, 100
    min_camera_z_abs = max(100, PLAYER_HEIGHT * 0.3)
    if key == GLUT_KEY_LEFT: camera_pos_list[0] -= move_speed
    elif key == GLUT_KEY_RIGHT: camera_pos_list[0] += move_speed
    elif key == GLUT_KEY_UP:
        if camera_pos_list[1] > 500 + zoom_speed : camera_pos_list[1] -= zoom_speed
        if camera_pos_list[2] > min_camera_z_abs + zoom_speed : camera_pos_list[2] -= zoom_speed
    elif key == GLUT_KEY_DOWN:
        if camera_pos_list[1] < 7000 - zoom_speed: camera_pos_list[1] += zoom_speed
        if camera_pos_list[2] < 7000 - zoom_speed: camera_pos_list[2] += zoom_speed
    camera_pos_list[0] = max(-BATTLEFIELD_SIZE, min(camera_pos_list[0], BATTLEFIELD_SIZE))
    camera_pos_list[1] = max(100, min(camera_pos_list[1], 7000))
    camera_pos_list[2] = max(min_camera_z_abs, min(camera_pos_list[2], 7000))

def mouseListener(button, state, m_x, m_y): 
    if state != GLUT_DOWN:  # Only trigger on button press, not release
        return
        
    if button == GLUT_LEFT_BUTTON:
        pause()
    elif button == GLUT_RIGHT_BUTTON:
        play()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 5.0, BATTLEFIELD_SIZE * 2.5)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(camera_pos_list[0], camera_pos_list[1], camera_pos_list[2], 0, 0, 0, 0, 0, 1)

def idle(): 
    global game_paused
    if game_paused:
        glutPostRedisplay()  # Still allow screen refreshes while paused
        return
    delta_time = get_delta_time() 
    global VajraAstra_cooldown_remaining_frames
    global current_frame_count
    current_frame_count += 1 # Increment frame counter for cooldowns
    
    if not modeOver:
        updateEnemySpawning(delta_time)
        moveEnemies()
        moveArrows()
        enemyShoot()
        updateAndProcessAgniAstras() # Update active AgniAstras  
        update_active_VajraAstras()
        updateBrahmastra(delta_time)
        updateMayastra(delta_time)  # Add this line
        update_pawan_astra()
        update_shield()
    else:
        moveArrows() 
        updateAndProcessAgniAstras() # Clear lingering AgniAstras 
        update_active_VajraAstras() 
    if VajraAstra_cooldown_remaining_frames > 0: 
        VajraAstra_cooldown_remaining_frames -= 1    
    
    glutPostRedisplay()
 

# Modify the showScreen function to draw Mayastra arrow and display its status
def showScreen():
    global camera_pos_list, brahmastra_state, brahmastra_last_used_time
    global mayastra_state, mayastra_last_used_time, mayastra_active_until
    
    if is_day: 
        glClearColor(0.5, 0.6, 0.8, 1)
    else: 
        glClearColor(0.0, 0.0, 0.1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    setupCamera()
    draw_battlefield()
    drawPlayer()
    draw_all_enemies()
    draw_shield()
    draw_pawan_astra() 

    # Draw regular arrows
    for arrow_data in Arrows:
        pos, direction = arrow_data['pos'], arrow_data['direction']
        if not (abs(direction[0]) < 0.001 and abs(direction[1]) < 0.001 and abs(direction[2]) < 0.001):
            drawArrow(pos[0], pos[1], pos[2], direction[0], direction[1], direction[2])
    
    # Draw active AgniAstras
    for AgniAstra_data in activeAgniAstras:
        drawAgniAstra(AgniAstra_data['pos'][0], AgniAstra_data['pos'][1], AgniAstra_data['pos'][2],
                     AgniAstra_data['radius'], AgniAstra_data['age_frames'])
 
    
    # Draw active VajraAstras 
    draw_all_active_VajraAstras()
    if VajraAstra_cooldown_remaining_frames > 0:
        drawText(10, WINDOW_HEIGHT - 150, f"VajraAstra : COOLDOWN ({VajraAstra_cooldown_remaining_frames/60.0:.1f}s) ")
    else:
        drawText(10, WINDOW_HEIGHT - 150, f"VajraAstra : READY (Press V)")
    

    # Draw Brahmastra arrow if it exists
    if brahmastra_arrow:
        pos, direction = brahmastra_arrow['pos'], brahmastra_arrow['direction']
        drawBrahmastraArrow(pos[0], pos[1], pos[2], direction[0], direction[1], direction[2])
    
    # Draw Mayastra arrow if it exists
    if mayastra_arrow:
        pos, direction = mayastra_arrow['pos'], mayastra_arrow['direction']
        drawMayastraArrow(pos[0], pos[1], pos[2], direction[0], direction[1], direction[2])

    # Display game status
    time_text = "Day" if is_day else "Night"
    drawText(10, WINDOW_HEIGHT - 30, f"Kurukshetra - {time_text}1")
    drawText(10, WINDOW_HEIGHT - 60, f"Life: {playerLife} | Score: {playerScore}")
    
    # Display Brahmastra status
    if brahmastra_state == "ready":
        brahmastra_text = "Brahmastra: READY (Press B)"
        brahmastra_color = (0.0, 1.0, 0.0)  # Green
    elif brahmastra_state == "firing":
        brahmastra_text = "Brahmastra: FIRING"
        brahmastra_color = (1.0, 0.5, 0.0)  # Orange
    else:  # cooldown
        cooldown_remaining = BRAHMASTRA_COOLDOWN - (time.time() - brahmastra_last_used_time)
        brahmastra_text = f"Brahmastra: COOLDOWN ({cooldown_remaining:.1f}s)"
        brahmastra_color = (1.0, 0.0, 0.0)  # Red
    
    # Set color for Brahmastra text
    glColor3f(*brahmastra_color)
    drawText(10, WINDOW_HEIGHT - 90, brahmastra_text)
    
    # Display Mayastra status
    current_time = time.time()
    if mayastra_state == "ready":
        mayastra_text = "Mayastra: READY (Press M)"
        mayastra_color = (0.0, 1.0, 0.0)  # Green
    elif mayastra_state == "firing":
        mayastra_text = "Mayastra: FIRING"
        mayastra_color = (0.0, 0.5, 1.0)  # Blue
    elif mayastra_state == "active":
        time_remaining = mayastra_active_until - current_time
        mayastra_text = f"Mayastra: ACTIVE ({time_remaining:.1f}s)"
        mayastra_color = (0.0, 0.7, 1.0)  # Light blue
    else:  # cooldown
        cooldown_remaining = MAYASTRA_COOLDOWN - (current_time - mayastra_last_used_time)
        mayastra_text = f"Mayastra: COOLDOWN ({cooldown_remaining:.1f}s)"
        mayastra_color = (1.0, 0.0, 0.0)  # Red
    
    # Set color for Mayastra text
    glColor3f(*mayastra_color)
    drawText(10, WINDOW_HEIGHT - 120, mayastra_text)
    
    # Reset color and draw controls text
    glColor3f(1.0, 1.0, 1.0)
    drawText(10, WINDOW_HEIGHT - 180, f"F : Agniastra | P: Pawanastra | H: Sheild | W-A-S-D: Move | T: Day/Night | R: Restart |") 
    drawText(10, WINDOW_HEIGHT - 210, f"Mouse Left Click : Pause | Mouse Right Click: Play")
    praise_text="Arjuna for a reason!Keep going"
    text_width_approx = len(praise_text) * 9
    text_x_coord = (WINDOW_WIDTH - text_width_approx) / 2
    text_y_coord = WINDOW_HEIGHT / 2
    if playerScore>=5000:
        playerWin=True
        drawText(int(text_x_coord), int(text_y_coord),praise_text )


    if modeOver:
        text = "GAME OVER! Arjun has to retrive. Press 'R' to Restart."
        text_width_approx = len(text) * 9
        text_x_coord = (WINDOW_WIDTH - text_width_approx) / 2
        text_y_coord = WINDOW_HEIGHT / 2
        # Draw background for text
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        gluOrtho2D(0,WINDOW_WIDTH,0,WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
        glColor3f(0.2,0.2,0.2)
        glRectf(text_x_coord - 20, text_y_coord - 20, text_x_coord + text_width_approx + 20, text_y_coord + 30)
        glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)
        # Draw text
        glColor3f(1,0.2,0.2)
        drawText(int(text_x_coord), int(text_y_coord), text)
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(525, 0) # Window position
    wind = glutCreateWindow(b"Kurukshetra - Battle with Divine Astras")
    if not wind:
     print("Failed to create window")
    

    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    print("Game Started with Enemy Spawning System!")
    print("Player Life:", playerLife, "| Max Enemies:", MAX_ENEMIES)
    print("WASD: Move Player | Arrow Keys: Move Camera | T: Day/Night | R: Restart Game")
    print("B: Brahmastra - Destroys all enemies (60s cooldown)")
    print("M: Mayastra - Redirects enemy arrows to attack enemies (40s cooldown)")
    print("Enemies will spawn automatically (5 per second) until reaching", MAX_ENEMIES)

    glutMainLoop()

if __name__ == "__main__":
    main()                                              