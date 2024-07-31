import math
import random  
import socket
import struct
import time
import pygame

def shift_this(number, high_first=True):
    """Utility method: extracts MSB and LSB from number.

    Args:
    number - number to shift
    high_first - MSB or LSB first (true / false)

    Returns:
    (high, low) - tuple with shifted values

    """
    low = (number & 0xFF)
    high = ((number >> 8) & 0xFF)
    if high_first:
        return((high, low))
    return((low, high))


def send_artnet_dmx(ip, universe, data, sequence):
    """
    Sends an ArtNet DMX packet to the specified IP and universe.

    Parameters:
        ip (str): The IP address of the ArtNet node.
        universe (int): The universe to which the data should be sent.
        data (bytes): The DMX data to send (up to 512 bytes).
    """
    ARTNET_PORT = 6454
    ARTNET_HEADER = b'Art-Net\x00'
    OP_OUTPUT = 0x5000
    PROTOCOL_VERSION = 14

    # Ensure the data is the right length
    if len(data) > 512:
        raise ValueError("DMX data exceeds 512 bytes")
    
    data_length = len(data)
    # data_padded = data + bytes(512 - data_length)

    # Construct the packet
    # packet = struct.pack(
    #     '!8sHHBBHHH512s',
    #     ARTNET_HEADER,       # 8-byte Art-Net header
    #     OP_OUTPUT,           # OpCode for DMX data
    #     PROTOCOL_VERSION,    # Protocol version
    #     0,                   # Sequence (set to 0 for no sequence tracking)
    #     0,                   # Physical port (set to 0)
    #     universe,            # Universe (Net and SubNet are combined)
    #     0,                   # Length high byte (always 0)
    #     data_length,         # Length low byte (actual data length)
    #     data_padded          # DMX data (padded to 512 bytes)
    # )
    #   """Make packet header."""
    # 0 - id (7 x bytes + Null)
    packet = bytearray()
    packet.extend(bytearray('Art-Net', 'utf8'))
    packet.append(0x0)
    # 8 - opcode (2 x 8 low byte first)
    packet.append(0x00)
    packet.append(0x50)  # ArtDmx data packet
    # 10 - prototocol version (2 x 8 high byte first)
    packet.append(0x0)
    packet.append(14)
    # 12 - sequence (int 8), NULL for not implemented
    packet.append(sequence)
    # 13 - physical port (int 8)
    packet.append(0x00)
    # 14 - universe, (2 x 8 low byte first)

    # if self.is_simplified:
        # not quite correct but good enough for most cases:
        # the whole net subnet is simplified
        # by transforming a single uint16 into its 8 bit parts
        # you will most likely not see any differences in small networks
    msb, lsb = shift_this(universe)   # convert to MSB / LSB
    packet.append(lsb)
    packet.append(msb)
    
    # # 14 - universe, subnet (2 x 4 bits each)
    # # 15 - net (7 bit value)
    # else:
    #     # as specified in Artnet 4 (remember to set the value manually after):
    #     # Bit 3  - 0 = Universe (1-16)
    #     # Bit 7  - 4 = Subnet (1-16)
    #     # Bit 14 - 8 = Net (1-128)
    #     # Bit 15     = 0
    #     # this means 16 * 16 * 128 = 32768 universes per port
    #     # a subnet is a group of 16 Universes
    #     # 16 subnets will make a net, there are 128 of them
    #     self.packet_header.append(self.subnet << 4 | self.universe)
    #     self.packet.append(self.net & 0xFF)

    # 16 - packet size (2 x 8 high byte first)
    msb, lsb = shift_this(data_length)		# convert to MSB / LSB
    packet.append(msb)
    packet.append(lsb)
    packet.extend(data)


    # Create the socket and send the packet
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(packet, (ip, ARTNET_PORT))
        # print(f"Sent {data_length} bytes of DMX data to {ip}:{universe}")


# draw the dot 
def comet(pos: int, color: (int, int, int)):
    r,g,b = 0,0,0
    if (pos <= 0) and (pos > -10):
        r = int(min( (10.0 + pos) / 10.0 * color[0], 255))
        g = int(min( (10.0 + pos) / 5.0 * color[1], 255))
        b = int(min( (10.0 + pos) / 3.0 * color[2], 255))
    return [r, g, b]
        

ip_address = "10.10.10.4"
universe = 1  # Universe 2
dmx_data = bytes([255] * 512)  # 512 channels at full intensity

# send_artnet_dmx(ip_address, universe, dmx_data)

clock = pygame.time.Clock()

class Dot: 
    def __init__(
        self,
        speed: float,
        startTime: int,
        startString: int,
        color: (int, int, int)
    ): 
        self.speed = speed
        self.startTime = startTime
        self.startString = startString
        self.color = color

dots = [
    Dot(-2, pygame.time.get_ticks(), 1, color = (255, 50, 50)),
    Dot(3, pygame.time.get_ticks(), 1, color =  (255, 50, 50)),
    Dot(2, pygame.time.get_ticks(), 2, color =  (155, 255, 50)),
    Dot(1, pygame.time.get_ticks(), 3, color =  (255, 100, 255)),
]

class LEDstring:
     def __init__(self, index: int, startX: int, startY: int, angle: int, leds: list): 
        self.index = index
        self.startX = startX
        self.startY = startY
        self.angle = angle
        self.leds = leds

# create_strings
LED_Strings = [
    LEDstring( index = 0, startX = 600, startY = 60, angle = 20, leds = list(range(1, 23))),
    LEDstring( 1, 400, 200, 70, leds = list(range(25, 28))),
    LEDstring( 2, 200, 680, 110, leds = list(range(29, 51))),
    LEDstring( 3, 100, 400, 90, leds = list(range(52, 65))),
    LEDstring( 4, 400, 800, 140, leds = list(range(80, 109))),
    # LEDstring( 5, 430, 800, 140, leds = list(range(81, 122))),
    LEDstring( 5, 460, 800, 140, leds = list(range(123, 172))),
    # LEDstring( 7, 490, 800, 140, leds = list(range(173, 183))),
    LEDstring( 6, 520, 800, 140, leds = list(range(184, 214))),
    LEDstring( 7, 550, 800, 140, leds = list(range(215, 244))),
    # LEDstring( 4, 400, 800, 140, list(range(245, 260))),  kaputt
    LEDstring( 8, 580, 800, 140, list(range(601, 623))),
    LEDstring( 9, 610, 800, 140, list(range(624, 657))),
    # LEDstring( 4, 400, 800, 140, list(range(624, 657))), kaputt
    LEDstring( 10, 640, 800, 140, list(range(665, 697))),
]

# Colors
colors = [pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(3)]

ledArray = []
for i in range(1000):
    ledArray.append([0, 0, 0])
    
# Initialize pygame
pygame.init()

display_info = pygame.display.Info()
# screen_width, screen_height = display_info.current_w, display_info.current_h
screen_width, screen_height = (800, 600)

# print(f"Screen resolution: {screen_width}x{screen_height}")

# Create the screen
# screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
screen = pygame.display.set_mode((screen_width, screen_height))

# Title and Icon
pygame.display.set_caption("Wokule LEDs")

# # Dot positions and velocities
# dots = [{'pos': [random.randint(0, screen_width), random.randint(0, screen_height)], 
#          'vel': [random.choice([-1, 1]), random.choice([-1, 1])],
#          'color': random.choice(colors)} for _ in range(100)]

# Main loop
running = True
start_time = pygame.time.get_ticks()
i=0
print(len(LED_Strings))

while running:
    # randomly create comets
    if random.randint(0, 100) < 10:
        LEDstring = random.randint(0, len(LED_Strings)-1)
        newdot = Dot(
                    random.uniform(0.3, 2.8),  # speed
                    pygame.time.get_ticks(),   # starttime
                    LEDstring,                 # the LED-string
                    [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)] # color
                )
        if (random.random()>0.5): 
            newdot.speed = -newdot.speed
        dots.append(newdot)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the LED-Array
    for index in range(1000):
        ledArray[index] = [0, 0, 0]

        
    for LED_String in LED_Strings:
        for dot in dots:
            if LED_String.index == dot.startString:
                if (dot.speed > 0):
                    pos = int( (pygame.time.get_ticks() - dot.startTime) / 50 * dot.speed) % 400

                    for index in range(len(LED_String.leds)):
                        c = comet(index - pos, dot.color)
                        ledArray[LED_String.leds[index]][0] = max( c[0], ledArray[LED_String.leds[index]][0])
                        ledArray[LED_String.leds[index]][1] = max( c[1], ledArray[LED_String.leds[index]][1])
                        ledArray[LED_String.leds[index]][2] = max( c[2], ledArray[LED_String.leds[index]][2])
                
                    if pos-10 > len(LED_String.leds):
                        # remove from dots
                        dots.remove(dot)

                else: # Dot is moving in opposite direction
                    pos = len(LED_String.leds)-int( (pygame.time.get_ticks() - dot.startTime) / 50 * - dot.speed) % 400

                    for index in range(len(LED_String.leds)):
                        c = comet(pos - index, dot.color)
                        ledArray[LED_String.leds[index]][0] = max( c[0], ledArray[LED_String.leds[index]][0])
                        ledArray[LED_String.leds[index]][1] = max( c[1], ledArray[LED_String.leds[index]][1])
                        ledArray[LED_String.leds[index]][2] = max( c[2], ledArray[LED_String.leds[index]][2])

                    if pos < -10:
                        
                        # remove from dots
                        dots.remove(dot)
                
    # Fill the screen with black
    screen.fill((0, 0, 0))
    i+=1

    # Draw the LEDs
    for LED_String in LED_Strings:

        # Update and draw dots
        i = 0
        for led in LED_String.leds:

            # calc position
            position = ( LED_String.startX + 20 * i * math.sin(LED_String.angle/360*2*math.pi), 
                         LED_String.startY + 20 * i * math.cos(LED_String.angle/360*2*math.pi) 
                       )
            i = (i + 1) % 256

            # Draw LEDs
            pygame.draw.circle(screen, ledArray[led], position, 4)

        # Update the display
        pygame.display.flip()

    # Control all LEDs
    data1 = bytearray([element for sublist in ledArray[:169] for element in sublist])
    send_artnet_dmx(ip="10.10.10.5", universe=1, data=data1, sequence=i)

    data2 = bytearray([element for sublist in ledArray[170:339] for element in sublist])
    send_artnet_dmx(ip="10.10.10.5", universe=2, data=data2, sequence=i)

    data3 = bytearray([element for sublist in ledArray[340:509] for element in sublist])
    send_artnet_dmx(ip="10.10.10.5", universe=3, data=data3, sequence=i)

    data4 = bytearray([element for sublist in ledArray[510:599] for element in sublist])
    send_artnet_dmx(ip="10.10.10.5", universe=4, data=data4, sequence=i)    

    data5 = bytearray([element for sublist in ledArray[600:697] for element in sublist])
    send_artnet_dmx(ip="10.10.10.5", universe=5, data=data5, sequence=i)  
    # Cap the frame rate
    clock.tick(30)

pygame.quit()