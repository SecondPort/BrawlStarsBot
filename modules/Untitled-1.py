# ... (Existing code from bot.py) ...

class Brawlbot:
    # In game tile width and height ratio with respect aspect ratio
    tile_w = 24
    tile_h = 17
    midpoint_offset = Constants.midpoint_offset

    # Map with sharp corners
    sharpCorner = Constants.sharpCorner
    # Either go to the closest bush to the player or the center
    centerOrder = Constants.centerOrder
    IGNORE_RADIUS = 0.5
    movement_screenshot = None
    screenshot = None
    INITIALIZING_SECONDS = 2
    results = []
    bushResult = []
    enemyResult = []
    counter = 0
    direction = ["top","bottom","right","left"]
    current_bush = None
    last_player_pos = None
    last_closest_enemy = None
    border_size = 1
    stopped = True
    topleft = None
    avg_fps = 0
    enemy_move_key = None
    timeFactor = 1
    
    # time to move increase by 5% if maps have sharps corner
    if sharpCorner: timeFactor = 1.05

    def __init__(self,windowSize,offsets,speed,attack_range) -> None:
        self.lock = Lock()
        
        # "brawler" chracteristic
        self.speed = speed
        # short range
        if attack_range >0 and attack_range <=4:
            range_multiplier = 1
            hide_multiplier = 1.3
        # medium range
        elif attack_range > 4 and attack_range <=7:
            range_multiplier = 0.85
            hide_multiplier = 1
        # long range
        elif attack_range > 7:
            range_multiplier = 0.8
            hide_multiplier = 0.8
        
        # attack range in tiles
        self.alert_range = attack_range + 2
        self.attack_range = range_multiplier*attack_range
        self.gadget_range = 0.9*self.attack_range
        self.hide_attack_range = 3.5 # visible to enemy in the bush
        self.HIDINGTIME = hide_multiplier * 23 # Increased hiding time for better hiding
        
        self.timestamp = time()
        self.window_w = windowSize[0]
        self.window_h = windowSize[1]
        self.center_window = (self.window_w / 2, int((self.window_h / 2)+ self.midpoint_offset))

        # tile size of the game
        # depended on the dimension of the game
        self.tileSize = round((round(self.window_w/self.tile_w)+round(self.window_h/self.tile_h))/2)
        self.state = BotState.INITIALIZING
        
        # offset
        self.offset_x = offsets[0]
        self.offset_y = offsets[1]

        #index
        self.player_index = 0
        self.bush_index = 1
        self.enemy_index = 2
        

    # ... (Rest of the existing methods) ...

    def find_bush(self):
        """
        sort the bush by distance and assigned it to self.bushResult
        :return: True or False (boolean)
        """
        bushes_found = False
        if self.results:
            bushes_found = len(self.results[self.bush_index]) > 0
            self.bushResult = self.ordered_bush_by_distance(self.bush_index)

        return bushes_found

    def move_to_bush(self):
        """
        find the moving time from the distance and the player's speed
        :return moveTime (float): The amount of time to move to the selected bush
        """
        # Prioritize closer bushes
        if self.bushResult:
            
            closest_bush = self.bushResult[0]
            
            x, y = closest_bush

            if not(self.results[self.player_index]):
                player_pos = self.center_window
            else:
                player_pos = self.results[self.player_index][0]
            
            tileDistance = self.tile_distance(player_pos,(x,y))
            
            # Avoid moving to bushes that are too close
            if tileDistance <= self.IGNORE_RADIUS:
                py.mouseUp(button=Constants.movement_key)
                print(f"Bush too close, ignoring: {tileDistance:.2f} tiles")
                return 0

            x,y = self.get_screen_position((x,y))
            py.mouseDown(button=Constants.movement_key,x=x, y=y)
            moveTime = tileDistance/self.speed
            moveTime = moveTime * self.timeFactor
            print(f"Distance: {round(tileDistance,2)} tiles")
            return moveTime

    # ... (attack, gadget, hold_movement_key remain the same) ...
    
    def stuck_random_movement(self):
        """
        Improved random movement when stuck
        """
        move_keys = ["w", "a", "s", "d"]
        random.shuffle(move_keys)  # Shuffle for more randomness

        for key in move_keys:
            with py.hold(key):
                sleep(random.uniform(0.5, 1.5)) # Vary hold time
                py.mouseUp(button=Constants.movement_key)

    def get_movement_key(self,index):
      # Rest of the method remains same
      # ...
      
    def enemy_random_movement(self):
        """
        Move player away from the enemy and attack
        """
        move_keys = self.get_movement_key(self.enemy_index)
        if move_keys:
            # Prioritize moving away from the enemy
            with py.hold(move_keys):
                py.press("e", presses=2, interval=0.4)
        else:
            # If no clear direction, move randomly and attack
            move_keys = ["w", "a", "s", "d"]
            random.shuffle(move_keys)
            for key in move_keys:
                with py.hold(key):
                    py.press("e", presses=2, interval=0.4)
                    sleep(random.uniform(0.2, 0.5))
                    break

    def enemy_distance(self):
        """
        Calculate the enemy distance from the player
        """
        enemy_dist = None
        if self.results:
            # player coordinate
            if self.results[self.player_index]:
                player_pos = self.results[self.player_index][0]
                # if player position in result is empty
                # assume that player is in the middle of the screen
            else:
                player_pos = self.center_window
            # enemy coordinate
            if self.results[self.enemy_index]:
                self.enemyResults = self.ordered_enemy_by_distance(self.enemy_index)
                if self.enemyResults:
                    enemy_dist = self.tile_distance(player_pos, self.enemyResults[0])
        return enemy_dist
    
    def is_enemy_in_range(self):
        """
        Check if enemy is in range of the player
        :return (boolean): True or False
        """
        enemyDistance = self.enemy_distance()
        if enemyDistance:
            # ranges in tiles
            if (enemyDistance > self.attack_range
                and enemyDistance <= self.alert_range):
                self.enemy_move_key = self.get_movement_key(self.enemy_index)
                return False
            elif (enemyDistance > self.gadget_range 
                  and enemyDistance <= self.attack_range):
                self.attack()
                return True
            elif enemyDistance <= self.gadget_range:
                self.gadget()
                self.attack()
                return True
        return False

    def is_enemy_close(self):
        #Rest of the method remain same
        # ...

    def is_player_damaged(self):
       # Rest of the method remain same
       # ...
    
    def have_stopped_moving(self):
        #Rest of the method remain same
        # ...

    def update_results(self,results):
        # Rest of the method remain same
        # ...
    
    def update_player(self,topleft,bottomright):
        # Rest of the method remain same
        # ...

    def update_screenshot(self, screenshot):
        # Rest of the method remain same
        # ...

    def start(self):
        # Rest of the method remain same
        # ...

    def stop(self):
        # Rest of the method remain same
        # ...

    def run(self):
        while not self.stopped:
            sleep(0.01)
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the startup waiting period is complete
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()

            elif self.state == BotState.SEARCHING:
                success = self.find_bush()
                #if bush is detected
                if success:
                    print("found bush")
                    self.moveTime = self.move_to_bush()
                    if self.moveTime > 0:
                        self.lock.acquire()
                        self.timestamp = time()
                        self.state = BotState.MOVING
                        self.lock.release()
                    else:
                        # Bush was too close, search again
                        self.lock.acquire()
                        self.state = BotState.SEARCHING
                        self.lock.release()
                #bush is not detected
                else:
                    print("Cannot find bush")
                    self.storm_random_movement()
                    # self.counter+=1
                
                if self.is_enemy_in_range():
                        self.lock.acquire()
                        self.state = BotState.ATTACKING
                        self.lock.release()

            elif self.state == BotState.MOVING:
                # when player is moving check if player is stuck
                if self.have_stopped_moving():
                    # cancel moving
                    py.mouseUp(button = Constants.movement_key)
                    self.stuck_random_movement()
                    # and search for bush again
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()
                #if player is stuck
                else:
                    sleep(0.15)

                if self.is_enemy_in_range():
                    py.mouseUp(button=Constants.movement_key)
                    self.lock.acquire()
                    self.state = BotState.ATTACKING
                    self.lock.release()
                # player successfully travel to the selected bush
                if time() > self.timestamp + self.moveTime:
                    py.mouseUp(button = Constants.movement_key)
                    print("Hiding")
                    self.lock.acquire()
                    # change state to hiding
                    self.timestamp = time()
                    self.state = BotState.HIDING
                    self.lock.release()
                    
            elif self.state == BotState.HIDING:
                
                
                if time() > self.timestamp + self.HIDINGTIME or self.is_player_damaged():
                    print("Changing state to search")
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()

                
                if self.is_enemy_close():
                    print("Enemy is nearby")
                    self.lock.acquire()
                    self.state = BotState.ATTACKING
                    self.lock.release()
                
            elif self.state == BotState.ATTACKING:
                if self.is_enemy_in_range():
                    self.enemy_random_movement()
                else:
                    if self.state == BotState.ATTACKING:
                        self.lock.acquire()
                        self.state = BotState.SEARCHING
                        self.lock.release()
                    
            self.fps = (1 / (time() - self.loop_time))
            self.loop_time = time()
            self.count += 1
            if self.count == 1:
                self.avg_fps = self.fps
            else:
                self.avg_fps = (self.avg_fps*self.count+self.fps)/(self.count + 1)