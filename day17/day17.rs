#![allow(unused)]
#![allow(dead_code)]
use std::fs;
use std::env;
use std::fmt;
use std::ops;
use std::collections::BinaryHeap;
use std::collections::HashSet;


#[derive(Debug, PartialEq, Eq, Clone, Copy)]
struct Direction {
    y: i32,
    x: i32,
}

impl Direction {
    fn new(y: i32, x: i32) -> Direction {
        // abs(x) + abs(y) == 1
        assert!(x.abs() + y.abs() == 1);
        Direction { y, x }
    }

    // rotate 90 degrees to the left
    // the result is a new direction
    fn rotate_left(&self) -> Direction {
        let newy = if self.y != 0 { 0 } else {if self.x == -1 { 1 } else { -1 } };
        let newx = if self.x != 0 { 0 } else {if self.y == 1 { 1 } else { -1 } };
        Direction::new(newy, newx)
    }

    // rotate 90 degrees to the right
    // the result is a new direction
    fn rotate_right(&self) -> Direction {
        let newy = if self.y != 0 { 0 } else {if self.x == -1 { -1 } else { 1 } };
        let newx = if self.x != 0 { 0 } else {if self.y == 1 { -1 } else { 1 } };
        Direction::new(newy, newx)
    }
}

impl fmt::Display for Direction {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let c = match (self.x, self.y) {
            (0, 1) => '^',
            (0, -1) => 'v',
            (1, 0) => '>',
            (-1, 0) => '<',
            _ => '?',
        };
        write!(f, "{}", c)
    }
}

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
struct Position {
    y: i32,
    x: i32,
}

impl fmt::Display for Position {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "({}, {})", self.y, self.x)
    }
}

impl Position {
    fn new(y: i32, x: i32) -> Position {
        Position { y, x }
    }
}

impl std::hash::Hash for Position {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.y.hash(state);
        self.x.hash(state);
    }
}

impl std::hash::Hash for Direction {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.y.hash(state);
        self.x.hash(state);
    }
}

impl ops::Add<Direction> for Position {
    type Output = Position;

    fn add(self, rhs: Direction) -> Position {
        Position::new(self.y + rhs.y, self.x + rhs.x)
    }
}

#[derive(Debug, Clone)]
struct State {
    cost: i64,
    position: Position,
    direction: Direction,
    count: u32,
}

// make State hashable
impl std::hash::Hash for State {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.position.hash(state);
        self.direction.hash(state);
        self.count.hash(state);
    }
}

impl PartialEq for State {
    fn eq(&self, other: &State) -> bool {
        self.position == other.position && self.direction == other.direction && self.count == other.count
    }
}

impl Eq for State {}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &State) -> Option<std::cmp::Ordering> {
        Some(other.cost.cmp(&self.cost)) // reversed since we only have maxheap
    }
}

impl Ord for State {
    fn cmp(&self, other: &State) -> std::cmp::Ordering {
        other.cost.cmp(&self.cost)
    }
}

fn solve(grid: &Vec<Vec<u8>>, destination: &Position, minmove: u32, maxmove: u32) -> Option<i64> {
    let mut heap = BinaryHeap::new();
    heap.push(State { cost: 0, position: Position::new(0, 0), direction: Direction::new(0, 1), count: 0 });
    heap.push(State { cost: 0, position: Position::new(0, 0), direction: Direction::new(1, 0), count: 0 });
    let height = grid.len() as i32;
    let width = grid[0].len() as i32;

    // create a set to keep track of visited positions
    // we cannot just use a fixed size grid, as we search in 4 dimensions
    // instead, hash the states
    let mut visited: HashSet<State> = HashSet::new();
    // create a closure to check whether position is inside grid
    let position_legal = |position: &Position| -> bool {
        position.y >= 0 && position.y < height && position.x >= 0 && position.x < width
    };
    assert!(position_legal(&Position::new(0, 0)));
    assert!(position_legal(&destination));

    while let Some(state) = heap.pop() {
        if visited.contains(&state) {
            continue;
        }
        // sleep for 1 second
        // std::thread::sleep(std::time::Duration::from_millis(1000));
        visited.insert(state.clone());

        if state.position == *destination && state.count >= minmove {
            return Some(state.cost);
        }

        if !position_legal(&state.position) {
            panic!("Illegal position: {}", state.position);
        }

        let forward = state.position + state.direction;
        if state.count < maxmove && position_legal(&forward) {
            let newcost = state.cost + (grid[forward.y as usize][forward.x as usize] as i64);
            heap.push(State { cost: newcost, position: forward, direction: state.direction, count: state.count + 1 });
        }

        if state.count < minmove {
            continue;
        }
        let left = state.direction.rotate_left();
        let right = state.direction.rotate_right();
        for direction in [left, right].iter() {
            let newpos = state.position + *direction;
            if position_legal(&newpos) {
                let newcost = state.cost + (grid[newpos.y as usize][newpos.x as usize] as i64);
                heap.push(State { cost: newcost, position: newpos, direction: *direction, count: 1 });
            }
        }

    }
    None
}

fn part1(lines: &Vec<&str>) -> Option<i64> {
    // lines is a vector of strings, each containing width numbers
    // we parse these numbers into a heightxwidth number matrix
    
    let height = lines.len();
    let width = lines[0].len();
    let mut grid: Vec<Vec<u8>> = vec![vec![0; width]; height];
    let height = height as i32;
    let width = width as i32;
    // parse lines of digits into grid where each digit belongs to one tile
    for (y, line) in lines.iter().enumerate() {
        for (x, c) in line.chars().enumerate() {
            grid[y][x] = c.to_digit(10).unwrap() as u8;
        }
    }
    let destination = Position::new(height - 1, width - 1);
    solve(&grid, &destination, 0, 3)
}

fn part2(lines: &Vec<&str>) -> Option<i64> {
    let height = lines.len();
    let width = lines[0].len();
    let mut grid: Vec<Vec<u8>> = vec![vec![0; width]; height];
    let height = height as i32;
    let width = width as i32;
    // parse lines of digits into grid where each digit belongs to one tile
    for (y, line) in lines.iter().enumerate() {
        for (x, c) in line.chars().enumerate() {
            grid[y][x] = c.to_digit(10).unwrap() as u8;
        }
    }
    let destination = Position::new(height - 1, width - 1);
    solve(&grid, &destination, 4, 10)
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
