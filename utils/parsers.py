def parse_input_file(file_path):
    """Parse input file into puzzle matrix"""
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    puzzle = []
    for line in lines:
        row = []
        for char in line:
            if char == '.':
                row.append(0)  # Empty cell
            else:
                try:
                    row.append(int(char))  # Island with number
                except ValueError:
                    row.append(0)  # Handle invalid characters as empty
        puzzle.append(row)
    
    return puzzle