#![allow(unused)]
#![allow(dead_code)]
use std::fs;
use std::env;

fn part1(lines: &Vec<&str>) -> Option<i64> {
    //TODO: implement me
    None
}

fn part2(lines: &Vec<&str>) -> Option<i64> {
    //TODO: implement me
    None
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
