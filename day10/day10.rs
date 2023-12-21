#![allow(unused)]
#![allow(dead_code)]
use std::fs;
use std::env;
use std::collections::{HashSet, VecDeque};

const NORTH: u8 = 0x1;
const EAST: u8 = 0x2;
const SOUTH: u8 = 0x4;
const WEST: u8 = 0x8;

#[derive(Hash, PartialEq, Eq, Debug, Clone, Copy)]
struct Position {
    x: usize,
    y: usize
}

impl Position {
    fn add(self, direction: u8) -> Position {
        let mut newy = self.y;
        let mut newx = self.x;
        if direction & NORTH != 0 {
            newy -= 1;
        }
        if direction & EAST != 0 {
            newx += 1;
        }
        if direction & SOUTH != 0 {
            newy += 1;
        }
        if direction & WEST != 0 {
            newx -= 1;
        }
        Position{x: newx, y: newy}
    }
}

fn connect(grid: &Vec<Vec<u8>>, pos1: Position, pos2: Position) -> bool {
    let ydiff = pos1.y.abs_diff(pos2.y);
    let xdiff = pos1.x.abs_diff(pos2.x);
    assert!(xdiff + ydiff == 1, "xdiff {} ydiff {}", xdiff, ydiff);
    if pos1.x > pos2.x {
        return grid[pos1.y][pos1.x] & WEST > 0 && grid[pos2.y][pos2.x] & EAST > 0;
    } else if (pos1.x < pos2.x) {
        return grid[pos2.y][pos2.x] & WEST > 0 && grid[pos1.y][pos1.x] & EAST > 0;
    } else if (pos1.y > pos2.y) {
        return grid[pos1.y][pos1.x] & NORTH > 0 && grid[pos2.y][pos2.x] & SOUTH > 0;
    } else if (pos2.y > pos1.y) {
        return grid[pos2.y][pos2.x] & NORTH > 0 && grid[pos1.y][pos1.x] & SOUTH > 0;
    }
    false
}

#[derive(Debug)]
struct QueueEntry {
    position: Position,
    steps: usize,
}


struct Grid {
    grid: Vec<Vec<u8>>,
    startposition: Position,
    width: usize,
    height: usize
}
use std::ops;
impl Grid {
    fn new(grid: Vec<Vec<u8>>, startposition: Position) -> Grid {
        let width = grid[0].len();
        let height = grid.len();
        Grid{grid, startposition, width, height}
    }
}

// accessing the grid with grid[5] shall return a reference the the Vec<u8> at index 5
impl ops::Index<usize> for Grid {
    type Output = Vec<u8>;

    fn index(&self, index: usize) -> &Self::Output {
        &self.grid[index]
    }
}

fn parsegrid(lines: &Vec<&str>) -> Option<Grid> {
    let mut grid: Vec<Vec<u8>> = vec![vec![0; lines[0].len()]; lines.len()];
    let height = grid.len();
    let width = grid[0].len();
    let mut startposition = None;
    for (y, line) in lines.iter().enumerate() {
        for (x, letter) in line.chars().enumerate() {
            let mut tile = match letter {
                '|' => NORTH | SOUTH,
                '-' => EAST | WEST,
                'L' => NORTH | EAST,
                'J' => NORTH | WEST,
                '7' => SOUTH | WEST,
                'F' => SOUTH | EAST,
                'S' => NORTH | EAST | SOUTH | WEST,
                '.' => 0,
                _ => panic!("{}", letter)
            };
            grid[y][x] = tile;  
            if letter == 'S' {
                startposition = Some(Position{x,y});
            }
        }
    }
    match startposition {
        Some(position) => Some(Grid::new(grid, position)),
        None => None
    }
}

struct Loop {
    diameter: usize,
    nodes: Vec<Position>,
    area: usize
}

impl Loop {
    fn new(diameter: usize, nodes: Vec<Position>) -> Loop {
        let area = Loop::calculate_area(&nodes);
        Loop{diameter, nodes, area}
    }

    fn calculate_area(nodes: &Vec<Position>) -> usize {
        // shoelace algorithm
        let mut area: isize = 0; // signed area
        let mut border: usize = 0; // border area
        for (i, &value) in nodes.iter().enumerate() {
            let nextpos = nodes[(i + 1) % nodes.len()];
            border += nextpos.y.abs_diff(value.y) + nextpos.x.abs_diff(value.x);
            area += (value.x * nextpos.y) as isize - (value.y * nextpos.x) as isize;
        }
        // also account for border, derived from Pick's theorem
        area.abs() as usize / 2 - (border - 1) / 2
    }
}

fn solve(lines: &Vec<&str>) -> Option<Loop> {
    // this function solves both part1 and part2
    let grid = parsegrid(lines).expect("Could not parse grid");
    let mut visited = HashSet::new();
    visited.insert(grid.startposition);
    let mut queue = VecDeque::new();
    queue.push_back(QueueEntry{position: grid.startposition, steps: 0});
    let position_valid = |position: Position| position.x < grid.width && position.y < grid.height;
    let mut maxstep = 0;
    let mut loopnodes1: Vec<Position> = Vec::new();
    let mut loopnodes2: Vec<Position> = Vec::new();
    let mut vecindex: u8 = 0;
    while let Some(current) = queue.pop_front() {
        maxstep = maxstep.max(current.steps);
        let pos = current.position;
        match vecindex {
            0 => loopnodes1.push(pos),
            1 => loopnodes2.push(pos),
            _ => panic!("We done goofed")
        };
        vecindex = 1 - vecindex; //toggle
        let directions = grid[current.position.y][current.position.x];
        let mut neighbors = Vec::new();
        if pos.y > 0 && directions & NORTH > 0 {
            neighbors.push(pos.add(NORTH));
        }
        if pos.x > 0 && directions & WEST > 0 {
            neighbors.push(pos.add(WEST));
        }
        if directions & EAST > 0 {
            neighbors.push(pos.add(EAST));
        }
        if directions & SOUTH > 0 {
            neighbors.push(pos.add(SOUTH));
        }
        for n in neighbors {
            if position_valid(n) && connect(&grid.grid, pos, n) && visited.insert(n) {
                queue.push_back(QueueEntry{position: n, steps: current.steps + 1});
            }
        }
    }
    // append loopnodes2 to loopnodes1 in reverse order
    for node in loopnodes2.iter().rev() {
        loopnodes1.push(*node);
    }
    Some(Loop::new(maxstep, loopnodes1))

}

fn part1(lines: &Vec<&str>) -> Option<i64> {
    Some(solve(lines).expect("Solver failed").diameter as i64)
}

fn part2(lines: &Vec<&str>) -> Option<i64> {
    //TODO: implement me
    Some(solve(lines).expect("Solver failed").area as i64)
}

fn main() {
    let args: Vec<String> =  env::args().collect();
    let infile = if args.len() == 1 { "input.txt" } else { &args[1] };

    let contents = fs::read_to_string(infile)
        .expect("Could not read in file");

    let lines: Vec<&str> = contents.lines().collect();

    // execute part 1 and part 2, print their results if they exist
    // later parts may follow, so we loop over the part functions
    let parts = [part1, part2];
    for (index, part) in parts.iter().enumerate() {
        let result = part(&lines);
        match result {
            Some(result) => println!("Part {}: {}", index+1, result),
            None => println!("Part {}: No result", index+1),
        }
    }
}
