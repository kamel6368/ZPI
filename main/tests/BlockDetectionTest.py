from main.block_detection import recogniseBlock
from main.Enums.Block import Block
from main.Enums.Shapes import Shape
import pytest

def test1():
    assert recogniseBlock(Shape.CIRCLE, Shape.CIRCLE, Shape.CIRCLE, Shape.CIRCLE) is Block.BALL
    assert recogniseBlock(Shape.SQUARE, Shape.SQUARE, Shape.SQUARE, Shape.SQUARE) is Block.CUBE
    assert recogniseBlock(Shape.SQUARE, Shape.TRAPEZIUM, Shape.TRIANGLE, Shape.CIRCLE) is Block.INVALID
    assert recogniseBlock(Shape.TRIANGLE, Shape.ISOSCELES_TRIANGLE, Shape.EQUILATERAL_TRIANGLE, Shape.ISOSCELES_TRIANGLE) is Block.PYRAMID
    assert recogniseBlock(Shape.SQUARE, Shape.RECTANGLE, Shape.RECTANGLE, Shape.SQUARE) is Block.CUBOID
    assert recogniseBlock(Shape.SQUARE, Shape.CIRCLE, Shape.SQUARE, Shape.CIRCLE) is Block.ROLLER

