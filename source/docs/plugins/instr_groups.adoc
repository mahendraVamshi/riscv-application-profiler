Grouping Instructions
=====================

We iterate through a list of all entries in the provided execution log and make a classify all the instructions into groups. The groups are defined by the following rules:

* If the instruction is a branch, it is placed in a group of its own.
* If the instruction is a memory instruction, it is placed in a group of its own.

The remaining instructions are placed in groups based on the following rules:

* If the instruction is a load instruction, it is placed in a group of its own.
* If the instruction is a store instruction, it is placed in a group of its own.
* If the instruction is a call instruction, it is placed in a group of its own.