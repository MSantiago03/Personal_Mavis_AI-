#coding: utf-8
#
# Copyright 2021 The Technical University of Denmark
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations
import sys

# pos_add and pos_sub are helper methods for performing element-wise addition and subtractions on positions
# Ex: Given two positions A = (1, 2) and B = (3, 4), pos_add(A, B) == (4, 6) and pos_sub(B, A) == (2,2)
from utils import pos_add, pos_sub
from typing import Union, Tuple
import domains.hospital.state as h_state

# A dictionary mapping action names to the corresponding direction deltas2
direction_deltas = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1),
}

# An action class must implement three types be a valid action:
# 1) is_applicable(self, agent_index, state) which return a boolean describing whether this action is valid for
#    the agent with 'agent_index' to perform in 'state' independently of any other action performed by other agents.
# 2) result(self, agent_index, state) which modifies the 'state' to incorporate the changes caused by the agent
#    performing the action. Since we *always* call both 'is_applicable' and 'conflicts' prior to calling 'result',
#    there is no need to check for correctness.
# 3) conflicts(self, agent_index, state) which returns information regarding potential conflicts with other actions
#    performed concurrently by other agents. More specifically, conflicts can occur with regard to the following
#    two invariants:
#    A) Two objects may not have the same destination.
#       Ex: '0  A1' where agent 0 performs Move(E) and agent 1 performs Push(W,W)
#    B) Two agents may not move the same box concurrently,
#       Ex: '0A1' where agent 0 performs Pull(W,W) and agent 1 performs Pull(E,E)
#    In order to check for these, the conflict method should return two lists:
#       a) destinations which contains all newly occupied cells.
#       b) moved_boxes which contains the current position of boxes moved during the action, i.e. their position
#          prior to being moved by the action.
# Note that 'agent_index' is the index of the agent in the state.agent_positions list which is often but *not always*
# the same as the numerical value of the agent character.


Position = Tuple[int, int] # Only for type hinting

class NoOpAction:

    def __init__(self):
        self.name = "NoOp"

    def is_applicable(self, agent_index: int,  state: h_state.HospitalState) -> bool:
        # Optimization. NoOp can never change the state if we only have a single agent
        return len(state.agent_positions) > 1

    def result(self, agent_index: int, state: h_state.HospitalState):
        pass

    def conflicts(self, agent_index: int, state: h_state.HospitalState) -> tuple[list[Position], list[Position]]:
        current_agent_position, _ = state.agent_positions[agent_index]
        destinations = [current_agent_position]
        boxes_moved = []
        return destinations, boxes_moved

    def __repr__(self) -> str:
        return self.name


class MoveAction:

    def __init__(self, agent_direction):
        self.agent_delta = direction_deltas.get(agent_direction)
        self.name = "Move(%s)" % agent_direction

    def calculate_positions(self, current_agent_position: Position) -> Position:
        return pos_add(current_agent_position, self.agent_delta)

    def is_applicable(self, agent_index: int,  state: h_state.HospitalState) -> bool:
        current_agent_position, _ = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)
        return state.free_at(new_agent_position)

    def result(self, agent_index: int, state: h_state.HospitalState):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)
        state.agent_positions[agent_index] = (new_agent_position, agent_char)

    def conflicts(self, agent_index: int, state: h_state.HospitalState) -> tuple[list[Position], list[Position]]:
        current_agent_position, _ = state.agent_positions[agent_index]
        new_agent_position = self.calculate_positions(current_agent_position)
        # New agent position is a destination because it is unoccupied before the action and occupied after the action.
        destinations = [new_agent_position]
        # Since a Move action never moves a box, we can just return the empty value.
        boxes_moved = []
        return destinations, boxes_moved

    def __repr__(self):
        return self.name

class PushAction:
    def __init__(self, agent_direction, box_direction):
       self.agent_delta = direction_deltas.get(agent_direction)
       self.box_delta = direction_deltas.get(box_direction)
       self.name = "Push(%s,%s)" % (agent_direction, box_direction)

        

    def calculate_agent_positions(self, current_agent_position: Position) -> Position:
        return pos_add(current_agent_position, self.agent_delta)
    

    def calculate_box_positions(self, current_box_position: Position) -> Position:
        return pos_add(current_box_position, self.box_delta)

   

    def is_applicable(self, agent_index: int, state: h_state.HospitalState) -> bool:
        current_agent_position, current_agent_char = state.agent_positions[agent_index]
        new_agent_position = self.calculate_agent_positions(current_agent_position) 
        current_box_position = new_agent_position
        box_index, current_box_char = state.box_at(current_box_position)
        new_box_position = self.calculate_box_positions(current_box_position)
        if state.box_at(current_box_position)[1] != '': 
            if state.level.colors[current_box_char] == state.level.colors[current_agent_char]:
                return state.free_at(new_box_position)
        return False
    
# Ok so what Lorenzo said to do is when we are checking if an action is applicable, we look at the 
# direction that we are pushing or pulling and then just check to see if there is a box that matches 
# up to what we want do to in that direction, and if so that just works then we do the same for result
# There is a helper function in actions  

    def result(self, agent_index: int, state: h_state.HospitalState):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        current_box_position = self.calculate_box_positions(current_agent_position)
        box_index = state.box_at(self.calculate_agent_positions(current_agent_position))[0]
        current_box_position, box_char = state.box_positions[box_index]
        new_agent_position = current_box_position 
        state.agent_positions[agent_index] = (new_agent_position, agent_char)
        new_box_position = self.calculate_box_positions(current_box_position)
        state.box_positions[box_index] = (new_box_position, box_char)

    def conflicts(self, agent_index: int, state: h_state.HospitalState) -> tuple[list[Position], list[Position]]:
        current_agent_position, _ = state.agent_positions[agent_index]
        new_agent_position = self.calculate_agent_positions(current_agent_position)
        current_box_position, _ = state.box_positions[state.box_at(self.calculate_agent_positions)[0]]
        new_box_position = self.calculate_box_positions(current_box_position)
        # New box position is a destination because it is unoccupied before the action and occupied after the action.
        destinations = []
        destinations.append(new_box_position)
        boxes_moved = []
        boxes_moved.append(current_box_position)
        return destinations, boxes_moved
    
    def __repr__(self):
        return self.name

    # Add PushAction here.. 

class PullAction:

    def __init__(self, agent_direction, box_direction):
        self.agent_delta = direction_deltas.get(agent_direction)
        self.box_delta = direction_deltas.get(box_direction)
        self.name = "Pull(%s,%s)" % (agent_direction, box_direction)

    def calculate_agent_positions(self, current_position: Position) -> Position:
        return pos_add(current_position, self.agent_delta)
    
    def calculate_box_positions(self, current_position: Position) -> Position:
        return pos_add(current_position, self.box_delta)
    
    
    def calculate_behind(self, current_position: Position) -> Position:
        return pos_sub(current_position, self.box_delta)
    
    def is_applicable(self, agent_index: int,  state: h_state.HospitalState) -> bool:    
        current_agent_position, current_agent_char = state.agent_positions[agent_index]
        new_agent_position = self.calculate_agent_positions(current_agent_position)
        current_box_position = self.calculate_behind(current_agent_position)
        if state.box_at(current_box_position)[1] != '': 
            box_index, current_box_char = state.box_at(current_box_position)
            if state.level.colors[current_box_char] == state.level.colors[current_agent_char]:
                if current_box_char == '' : return False
                return state.free_at(new_agent_position)
        return False


    def result(self, agent_index: int, state: h_state.HospitalState):
        current_agent_position, agent_char = state.agent_positions[agent_index]
        new_agent_position = self.calculate_agent_positions(current_agent_position)
        current_box_position = self.calculate_behind(current_agent_position)
        box_index, box_char = state.box_at(current_box_position)
        new_box_position = current_agent_position
        state.agent_positions[agent_index] = (new_agent_position, agent_char)
        state.box_positions[box_index] = (new_box_position, box_char)



    def conflicts(self, agent_index: int, state: h_state.HospitalState) -> tuple[list[Position], list[Position]]:
        current_agent_position, _ = state.agent_positions[agent_index]
        new_agent_position = self.calculate_agent_positions(current_agent_position)
        current_box_position, _ = state.box_positions[state.box_at(self.calculate_behind)[0]]
        new_box_position = current_agent_position
        # New agent position is a destination because it is unoccupied before the action and occupied after the action.
        destinations = []
        destinations.append(new_agent_position)
        boxes_moved = []
        boxes_moved.append(current_box_position)
        return destinations, boxes_moved
    

        

    def __repr__(self):
        return self.name


AnyAction = Union[NoOpAction, MoveAction] # Only for type hinting


# An action library for the multi agent pathfinding domain using the Move action you implemented

DEFAULT_MAPF_ACTION_LIBRARY = [
    NoOpAction(),
    MoveAction("N"),
    MoveAction("S"),
    MoveAction("E"),
    MoveAction("W"),
    
    
]


# An action library for the full hospital domain using the Push and Pull actions you implemented
DEFAULT_HOSPITAL_ACTION_LIBRARY = [
    NoOpAction(),
    MoveAction("N"),
    MoveAction("S"),
    MoveAction("E"),
    MoveAction("W"),
    PushAction("N","N"),
    PushAction("N","E"),
    PushAction("N","W"),
    PushAction("S","S"),
    PushAction("S","E"),
    PushAction("S","W"),
    PushAction("E","N"),
    PushAction("E","S"),
    PushAction("E","E"),
    PushAction("W","N"),
    PushAction("W","S"),
    PushAction("W","W"),
    PullAction("N","N"),
    PullAction("N","E"),
    PullAction("N","W"),
    PullAction("S","S"),
    PullAction("S","E"),
    PullAction("S","W"),
    PullAction("E","N"),
    PullAction("E","S"),
    PullAction("E","E"),
    PullAction("W","N"),
    PullAction("W","S"),
    PullAction("W","W"), 
 ]

