from __future__ import annotations
from re import X
from typing import Optional
from a2_support import UserInterface, TextInterface
from constants import *

__author__ = "Muhammad Khan, 47511921"
__email__ = "m.khan2@uqconnect.edu.au"

__version__ = 1.0


def load_game(filename: str) -> list['Level']:
    """ Reads a game file and creates a list of all the levels in order.
    
    Parameters:
        filename: The path to the game file

    Returns:
        A list of all Level instances to play in the game
    """
    levels = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('Maze'):
                _, _, dimensions = line[5:].partition(' - ')
                dimensions = [int(item) for item in dimensions.split()]
                levels.append(Level(dimensions))
            elif len(line) > 0 and len(levels) > 0:
                levels[-1].add_row(line)
    return levels


class Tile(object):
    """ Abstract superclass, represents the floor for a (row, column) position.
        Provides all methods for the subclasses, although some are overwritten.
    """
    def __init__(self):
        """ Init method to set the stats of each tile, is overwritten to change
            the blocking, damage and id values.
        """
        self._is_blocking = False
        self._damage = 0
        self._id = 'AT'

    def is_blocking(self) -> bool:
        """ Method that checks if a tile is blocking.

        Returns:
            self._is_blocking: True or False to confirm or deny if the tile is blocking True means
            tile is blocking false means tile is not blocking
        """
        return self._is_blocking

    def damage(self) -> int:
        """ Getter method to check the private self._damage stat from outside 
            the class.

        Returns:
            The self._damage value (int) for the Tile instance
        """
        return self._damage

    def get_id(self) -> str:
        """ Getter method to check the private self._id of a tile form outside
            the class.

        Returns: the self._id (str) for the Tile instance
        """
        return self._id

    def __str__(self) -> str:
        """
        Returns: 
            The string representation for this Tile.
        """
        return str(self._id)

    def __repr__(self) -> str:
        """
        Returns:
            (str): The text that would be required to create a new instance of
            this class.
        """
        return f'{type(self).__name__}()'


class Wall(Tile):
    """ Subclass of tile, with blocking value to be true.
    """
    def __init__(self):
        super().__init__()
        self._is_blocking = True
        self._id = WALL


class Empty(Tile):
    """ A subclass of tile that does not contain anything.
    """
    def __init__(self):
        super().__init__()
        self._id = EMPTY


class Lava(Tile):
    """ A subclass of tile that is not blocking but does 5 damage to the player
        HP.
    """
    def __init__(self):
        """
        in
        """
        super().__init__()
        self._damage = LAVA_DAMAGE
        self._id = LAVA


class Door(Tile):
    """ A subclass of tile that can be either blocking or unblocking depending
        on the state.
    """
    def __init__(self):
        super().__init__()
        self._is_blocking = True
        self._id = DOOR

    def unlock(self) -> None:
        """ Method that changes the state of the door to go from blocking to
        unblocking
        """
        self._id = EMPTY
        self._is_blocking = False


class Entity(object):
    """ Entity class is the abstract class that provides the functionality for
        all entities within the game.
    """
    def __init__(self, position: tuple[(int, int)]):
        """ Sets up the initial conditions of the Entity object.

        Parameters:
            position: Position that the entity will appear in the maze, (row,
                      column)
        """
        self._position = position
        self._id = 'E'

    def get_position(self) -> tuple:
        """ Getter method that checks the current position of an entity object.

        Returns:
            self._position (tuple): Private variable storing the position of the
                                    entity
        """
        return self._position

    def get_name(self) -> str:
        """ Getter method that checks the name of the class to which the entity
            belongs.

        Returns:
            type(self).__name__ (str): Name of the class the entity belongs to
        """
        return type(self).__name__

    def get_id(self) -> str:
        """ Getter method to check the id of the entity instance.

        Returns:
            self._id (str): Private variable that stores the id value of the
                            object.
        """
        return self._id

    def __str__(self) -> str:
        
        return str(self._id)

    def __repr__(self) -> str:
        """
        Returns:
            (str): The text that would be required to make a new instance of
                   this class that looks identical
        """
        return f'{type(self).__name__}({self._position})'


class DynamicEntity(Entity):
    """ A subclass of Entity that provides base functionality for entities that
        are dynamic (can change position). Inherits from Entity.
    """

    def set_position(self, new_position: tuple[(int, int)]) -> None:
        """ Setter method that updates the entity's position

        Parameters:
             new_position (tuple): the new position(row, column) that the entity
             is to move to
        """
        self._position = new_position


class Player(DynamicEntity):
    """ Subclass of Dynamic Entity that is controlled by the user, and must move
        from the start position to the end of the maze. Inherits from
        Dynamic_Entity.
    """

    def __init__(self, position: tuple[int, int]):
        """ Sets up th default stats of the player, that is minimum hunger and
            thirst but maximum health.

        Parameters:
            position (tuple): the initial position(row, column) of the player
        """
        super().__init__(position)
        self._health = 100
        self._hunger = 0
        self._thirst = 0
        self._items = []
        self._id = 'P'
        self._items = Inventory()
        self._position = position

    def get_hunger(self) -> int:
        """ Getter method to check hunger status from outside the class.

        Returns:
            self._hunger (int): Private variable that stores the hunger stat of
                                the player
        """
        return self._hunger

    def get_thirst(self) -> int:
        """ Getter method to check the thirst from outside the class.

        Returns:
            self._thirst (int): Private variable that stores the thirst stat of
                                the player
        """
        return self._thirst

    def get_health(self) -> int:
        """ Getter method to check the health from outside the class.

        Returns:
            self._health (int): Private variable that stores the health stat of
                                the player
        """
        return self._health

    def change_position(self, new_position: tuple[int, int]) -> None:
        """ Setter method to change the position of the player from outside the
            class instance.

        Parameters:
            new_position (tuple): Position the player is to be updated to.
        """
        self._position = new_position

    def change_stat(self, stat, amount: int, maxi: int) -> int:
        """ Abstraction method of the following three methods. Changes a value
            of a player stat (hunger, thirst or health) by a certain amount,
            also caps the stats at a certian amount.

        Parameters:
            stat (stat): The stat to be changed (hunger, thirst or health)
            amount (int): How much to change the stat by.
            maxi (int): Maximum allowed value for stat.

        Returns:
            stat: The updated value of the stat after being changed.
        """
        if (stat + amount) in range(0, maxi):
            stat += amount

        elif (stat + amount) >= maxi:
            stat = maxi

        elif (stat + amount) <= 0:
            stat = 0

        return stat

    def change_hunger(self, amount: int) -> None:
        """ Setter method that alters the players hunger status by a given
            amount, calls the change_stat method for all functionality.

        Parameters
            amount: The number of hunger points to restore or remove, depending
                    on what food is used
        """
        self._hunger = self.change_stat(self._hunger, amount, MAX_HUNGER)

    def change_thirst(self, amount: int) -> None:
        """ Setter method that alters the players thirst status by a given
            amount, calls the change_stat method for all functionality.

        Parameters
            amount: The number of thirst points to restore or remove
        """
        self._thirst = self.change_stat(self._thirst, amount, MAX_THIRST)

    def change_health(self, amount: int) -> None:
        """ Setter method that alters the players health status by a given
            amount, calls the change_stat method for all functionality.

        Parameters
            amount: The number of health points to restore or remove
        """
        self._health = self.change_stat(self._health, amount, MAX_HEALTH)

    def get_inventory(self) -> Inventory:
        """ Getter method that checks the inventory instance of a player.

        Returns:
            self._items (inventory): An inventory instance that shows the
                                    current items
        """
        return self._items

    def add_item(self, item: Item) -> None:
        """ Method that adds an item to the inventory instance of the player.

        Parameters
            item (Item): Item object to be added to the inventory
        """
        self._items.add_item(item)


class Item(Entity):
    """ Subclass of entity that provides the functionality of items within the
        game.
    """

    def __init__(self, position):
        super().__init__(position)
        self._id = 'I'

    def apply(self, player: Player) -> None:
        raise NotImplementedError


class Potion(Item):
    """ Subclass of Item, an item that restores health when applied.
    """

    def __init__(self, position):
        super().__init__(position)
        self._id = POTION

    def apply(self, player: Player) -> None:
        """ Method that uses the item, overwrites the superclass method to not
            raise NotImplementedError and to change a player health instead.

        Parameters
            player (Player): the player object that the item will affect
                """
        player.change_health(POTION_AMOUNT)


class Coin(Item):
    """ Subclass of item, can be picked up but not used, and the maze does not
        end until all coins are picked up.
    """

    def __init__(self, position):
        super().__init__(position)
        self._id = COIN

    def apply(self, player: Player) -> None:
        """ Method that uses the item, overwrites the superclass method to not
            raise NotImplementedError and to None instead.

        Parameters
            player (Player): the player object that the item will affect
                """
        return None


class Water(Item):
    """ Subclass of item that restores thirst when used.
    """

    def __init__(self, position):
        super().__init__(position)
        self._id = WATER

    def apply(self, player: Player) -> None:
        """ Method that uses the item, overwrites the superclass method to not
            raise NotImplementedError and to change a players thirst instead.

        Parameters
            player (Player): the player object that the item will affect
                """
        player.change_thirst(WATER_AMOUNT)


class Food(Item):
    """ Subclass of item that restores hunger when used, different foods restore
        a different amount.
    """

    def __init__(self, position):
        super().__init__(position)
        self._id = 'F'

    def apply(self, player: Player) -> None:
        """ Method that uses the item, overwrites the superclass method to not
                    raise NotImplementedError and to None instead.

                Parameters
                    player (Player): the player object that the item will affect
        """
        return None


class Apple(Food):
    """ Subclass of food that restores 1 hunger point.
    """

    def __init__(self, position):
        super().__init__(position)
        self._id = APPLE
        self._stat = APPLE_AMOUNT

    def apply(self, player) -> None:
        """ Method that uses the item, overwrites the superclass method to not
                    return None and to change hunger points by reducing 1
                    instead.

                Parameters
                    player (Player): the player object that the item will affect
                        """
        player.change_hunger(self._stat)


class Honey(Food):
    """ Subclass of food that restores 5 hunger points.
    """

    def __init__(self, position):
        super().__init__(position)
        self._id = HONEY
        self._stat = HONEY_AMOUNT

    def apply(self, player) -> None:
        """ Method that uses the item, overwrites the superclass method to not
                    return None and to change hunger points by reducing 5
                    instead.

                Parameters
                    player (Player): the player object that the item will affect
                        """
        player.change_hunger(self._stat)


class Inventory(object):
    """ A class that is used by the player to contain and manage a collection of
    items obtained throughout the game. Can be changed over the course of game.
    """

    def __init__(self, initial_items: Optional[list[Item]] = []) -> None:
        """ Sets up the inventory with any optional initial items stated.

        Parameters:
             initial_items (list): Optional  list parameter to add initial items
                                   to the inventory to make adding onto the
                                   inventory easier
        """
        self._items = initial_items
        self._inventory = self.get_items()

    def add_item(self, item: Item) -> None:
        """ Method that adds an item to the inventory.

        Parameters
            item (Item): Item to be added to inventory instance
        """
        self._items.append(item)

    def get_items(self) -> dict[str, list[Item]]:
        """ Getter method to check the inventory and see all the current items
           within the current instance.

        Returns:
             self._inventory (dict): a private variable that is easy to read for
                                    the user and represents the items within
                                    the inventory
        """
        self._inventory = {}

        if self._items is not None:
            # adds item as key if first instance, else adds the item as a value
            for item in self._items:
                if item.get_name() not in self._inventory.keys():
                    self._inventory[item.get_name()] = [item]

                elif item.get_name() in self._inventory.keys():
                    self._inventory[item.get_name()] += [item]

        return self._inventory

    def remove_item(self, item_name: str) -> Optional[Item]:
        """ Method to remove an item from the inventory.

        Parameters:
              item_name (str): Name of the item to be removed

        Returns:
             item (Item): The item that has been removed from the inventory
                    (optional as an item may not necessarily have been removed)
        """
        for item in self._items:
            if item_name == type(item).__name__:
                self._items.remove(item)
                return item

    def __str__(self) -> str:
        """
        Returns: A string containing information about quantities of items
                 available in the inventory
        """
        items = []
        for item in self._inventory.keys():
            items.append(f'{item}: {len(self._inventory[item])}')
        return '\n'.join(items)

    def __repr__(self):
        """
        Returns: A string that could be used to construct a new instance of
                 Inventory containing the same items as self currently contains
        """
        return f"Inventory(initial_items = {self._items})"


class Maze(object):
    """ A class that represents the space in which a level takes place. Does not
        know where entities are, only knows walls and dimensions.
    """

    def __init__(self, dimensions: tuple[int, int]) -> None:
        """ Sets up the maze object with initial dimensions.

        Parameters:
             dimensions (tuple): Dimensions of the maze (rows, columns)
        """
        self._rows = dimensions[0]
        self._columns = dimensions[1]
        self._maze = []
        self._maze_ids = []
        self._row = []
        self._row_ids = []

    def get_dimensions(self) -> tuple[int, int]:
        """ Getter method to check the rows and columns from outside the class.

        Returns:
             dimensions (tuple): Dimensions of the maze (rows, columns)
        """
        return self._rows, self._columns

    def get_ids(self) -> list:
        """ Getter method that returns the maze tile ids.

        Returns:
             self._maze_ids (list): A list of lists that shows the ids of each
                                tile and their respective position in the maze.
        """
        return self._maze_ids

    def add_row(self, row: str) -> None:
        """ Method to add row to the maze.

        Preconditions:
                Number of rows must not exceed the dimensions specified in Maze.

        Parameters:
            row (str): The row instance to be added
        """
        self._row = []
        self._row_ids = []

        for tile in row:
            self._row_ids.append(tile)

            # checks which tile is added
            if tile.lower() == DOOR.lower():
                tile = Door()

            elif tile.lower() == LAVA.lower():
                tile = Lava()

            elif tile == WALL.lower():
                tile = Wall()

            else:
                tile = Empty()

            self._row.append(tile)

        self._maze.append(self._row)
        self._maze_ids.append(self._row_ids)

    def unlock_door(self) -> None:
        """ Method to change the state of the door from being locked to
            unlocked, that is self._is_blocking becomes false and the
            tile_id is altered.
        """
        for row in self._maze:
            for tile in row:
                if tile.get_id() == 'D':
                    row[row.index(tile)].unlock()

    def get_tiles(self) -> list[list[Tile]]:
        """ Getter method to check the tiles within the maze.

        Returns:
            self._maze (Maze): The private variable that stores the tiles of the
                               maze instance
        """
        return self._maze

    def get_tile(self, position: tuple[int, int]) -> Tile:
        """ Method that returns the tile object at a specific position.

        Parameters:
            position (tuple): Position of tile to be found

        Returns:
            tile: Tile instance at the given position.
        """
        row = position[0]
        column = position[1]
        return (self._maze[row])[column]

    def __str__(self) -> str:
        """
        Returns:
            String representation of this maze. Each line in the output is a row
            in the maze (each Tile instance is represented by its ID).
        """
        self._rep = []

        for row in self._maze:
            self._reps = []

            for tile in row:
                self._reps.append(''.join(tile.get_id()))

            self._rep.append(''.join(self._reps))

        return '\n'.join(self._rep)

    def __repr__(self) -> str:
        """
        Returns:
            String that could be copied and pasted to construct a new Maze
            instance with the same dimensions as this Maze instance.
        """
        return f'Maze(({self._rows}, {self._columns}))'


class Level(object):
    def __init__(self, dimensions: tuple[int, int]) -> None:
        self._rows = dimensions[0]
        self._columns = dimensions[1]
        self._maze = Maze((self._rows, self._columns))
        self._player_start = None
        self._items = {}

    def get_maze(self) -> Maze:
        return self._maze

    def get_dimensions(self) -> tuple[int, int]:
        return self._rows, self._columns

    def attempt_unlock_door(self) -> None:
        for item in self._items.values():
            if type(item).__name__ == 'Coin':
                return

        self._maze.unlock_door()
        return

    def remove_item(self, position: tuple[int, int]) -> None:
        for item in self._items.keys():
            if item == position:
                del self._items[item]
                return

    def add_player_start(self, position: tuple[int, int]) -> None:
        self._player_start = position
        return

    def add_entity(self, position: tuple[int, int], entity_id: str) -> None:
        x = position
        for i in [Water(x), Honey(x), Apple(x), Coin(x), Potion(x), Player(x)]:
            if i.get_id() == entity_id:
                entity = i
        self._items[x] = entity

    def add_row(self, row: str) -> None:
        self._maze.add_row(row)
        self._items = {}

        # adds items that are not contained within self._maze
        for row in self._maze.get_ids():
            for item in row:
                position = ((self._maze.get_ids().index(row)), row.index(item))

                if item.lower() in ['m', 'a', 'c', 'h']:
                    self.add_entity(position, item)
                    self._maze.get_ids()[position[0]][position[1]] = item

                if item.lower() == 'p':
                    self.add_player_start(position)

    def get_items(self) -> dict[tuple[int, int], Item]:
        return self._items

    def get_player_start(self) -> Optional[tuple[int, int]]:
        return self._player_start

    def __str__(self) -> str:
        return f'Maze: {(Maze.__str__(self._maze))}\nItems: {self._items}\n' \
               f'Player start: {self._player_start}'

    def __repr__(self) -> str:
        return f'Level(({self._rows}, {self._columns}))'


class Model(object):
    def __init__(self, game_file: str) -> None:
        self._levels = load_game(game_file)
        self._levels_left = len(self._levels)
        self._levels_completed = 0
        self._player = Player(Model.get_level(self).get_player_start())
        self._won = False
        self._lost = False
        self._level_up = False
        self._moves_made = 0

    def has_won(self) -> bool:
        if self._levels_left == 0:
            self._won = True

        return self._won

    def has_lost(self) -> bool:
        for i in [self._player.get_hunger(), self._player.get_thirst()]:
            if i == 10:
                self._lost = True

        if self._player.get_health() == 0:
            self._lost = True

        return self._lost

    def get_level(self) -> None:
        return self._levels[self._levels_completed]

    def level_up(self) -> bool:
        self._levels_completed += 1
        self._levels_left -= 1
        self._level_up = True

        if self._levels_left > 0:
            self._player.set_position(self.get_level().get_player_start())

    def did_level_up(self) -> bool:
        return self._level_up

    def move_player(self, delta: tuple[int, int]) -> None:
        self._level_up = False
        position = (self._player.get_position()[0] + delta[0],
                    self._player.get_position()[1] + delta[1])
        tile = self.get_level().get_maze().get_tile(position)

        if tile.is_blocking() is False:
            if tile.get_id() == LAVA:
                self._player.change_health(-5)
            self._player.set_position(position)
            self._moves_made += 1
            self._player.change_health(-1)

        if type(tile).__name__ == 'Door' and tile.is_blocking() is False:
            self._level_up()

        if (self._moves_made // 5) == 0:
            self._player.change_thirst(1)
            self._player.change_hunger(1)

        self.attempt_collect_item(position)

    def attempt_collect_item(self, position: tuple[int, int]) -> None:
        
        if position in self.get_level().get_items():
            # if the given position contains ann item, the item is added
            self._player.add_item(self.get_level().get_items()[position])
            self.get_level().get_maze().get_ids()[position[0]][position[1]] = \
                ' '

        # this section makes sure that if all coins are collected, door unlocks
        count_coin = 0
        for row in self.get_current_maze().get_tiles():
            for item in row:
                if type(item).__name__ == "Coin":
                    count_coin += 1

        if len(self._player.get_inventory().get_items()['Coin']) == count_coin:
            self.get_level().attemp_unlock_door()

    def get_player(self) -> Player:
        return self._player

    def get_player_stats(self) -> tuple[int, int, int]:
        return self._player.get_health(), self._player.get_hunger(), \
               self._player.get_thirst()

    def get_player_inventory(self) -> Inventory:
        return self._player.get_inventory()

    def get_current_maze(self) -> Maze:
        return self.get_level().get_maze()

    # ran out of time here RIP
    def get_current_items(self) -> dict[tuple[int, int], Item]:
        pass

    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        pass


class MazeRunner(object):
    def __init__(self, game_file: str, view: UserInterface) -> None:
        pass

    def play(self) -> None:
        play_game.exe


def main():
    pass


if __name__ == '__main__':
    main()
