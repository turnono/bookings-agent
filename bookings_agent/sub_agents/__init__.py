# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sub-agents package initialization."""

# Create empty directories for our agents if they don't exist
import os
import pathlib

# Get the directory where this __init__.py file is located
current_dir = pathlib.Path(__file__).parent.absolute()

# Create the booking_validator directory if it doesn't exist
booking_validator_dir = current_dir / "booking_validator"
os.makedirs(booking_validator_dir, exist_ok=True)

# Create an __init__.py file in the booking_validator directory if it doesn't exist
booking_validator_init = booking_validator_dir / "__init__.py"
if not booking_validator_init.exists():
    with open(booking_validator_init, "w") as f:
        f.write('"""Booking Validator Agent package."""\n')

