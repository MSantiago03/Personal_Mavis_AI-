# coding: utf-8
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
import itertools
from utils import pos_add, pos_sub, APPROX_INFINITY
from collections import deque, defaultdict

import domains.hospital.state as h_state
import domains.hospital.goal_description as h_goal_description
import domains.hospital.level as h_level

class HospitalGoalCountHeuristics:

    # Write your own implementation of the goal count heuristics here. Remember that the goal count heuristics is simply the number of goals that are not satisfied in the current state. 

    def __init__(self):
        self.state = h_state
        
        pass

    def preprocess(self, level: h_level.HospitalLevel):
        # This function will be called a single time prior to the search allowing us to preprocess the level such as
        # pre-computing lookup tables or other acceleration structures
        pass

    def h(self, state: h_state.HospitalState, goal_description: h_goal_description.HospitalGoalDescription) -> int:
            goal_num = len(goal_description.goals)
            for (goal_position, goal_char, is_positive_literal) in goal_description.goals:
                char = state.box_at(goal_position)
                if goal_char == char:
                     goal_num -= 1

            return goal_num


class HospitalAdvancedHeuristics:

    # Write your own implementation of the advanced heuristics here.

    def __init__(self):
        self.distances = None
        self.goal_chars = None
        self.agent_chars = None
        self.goals = None

        self.state = h_state

        pass

    def preprocess(self, level: h_level.HospitalLevel):
        # This function will be called a single time prior to the search allowing us to preprocess the level such as
        # pre-computing lookup tables or other acceleration structures
        pass

    def h(self, state: h_state.HospitalState, goal_description: h_goal_description.HospitalGoalDescription):
        manhattan_distance = 0

        n = len(goal_description.box_goals)
        for i in range(0, n):
            

            box_x_value = state.box_positions[i][0][0]
            box_y_value = state.box_positions[i][0][1]

            box_goal_x_value = goal_description.box_goals[i][0][0]
            box_goal_y_value = goal_description.box_goals[i][0][1]
            

            manhattan_distance += abs(box_x_value - box_goal_x_value) + abs(box_y_value - box_goal_y_value)
        

        return manhattan_distance
 