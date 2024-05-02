import argparse
import csv
import re
import sys
from collections import OrderedDict
from typing import Generator, List, Optional, Tuple, Union


def find_index_of_regex(cols: List[str], regex: str) -> Optional[int]:
    """Find the index of the first element that matches the regex."""
    pattern = re.compile(regex)
    for i, col in enumerate(cols):
        if pattern.match(col):
            return i
    return None


def pop_next_tuple(cols: List[str]) -> Optional[List[str]]:
    """Pop the next tuple from the list of columns."""
    index_a = find_index_of_regex(cols, r"^src=.*")
    index_b = find_index_of_regex(cols, r"^bytes=.*")
    if index_a is not None and index_b is not None:
        data = cols[index_a:index_b+1]
        del cols[index_a:index_b+1]
        return data
    return None


def pop_all_attrs_iter(cols: List[str]) -> Generator[str, None, None]:
    """Pop all attributes from the list of columns."""
    while True:
        index = find_index_of_regex(cols, r"^.*=")
        if index is not None:
            data = cols[index]
            del cols[index]
            yield data
            continue
        return


def pop_all_attrs(cols: List[str]) -> List[str]:
    """Pop all attributes from the list of columns."""
    return list(pop_all_attrs_iter(cols))


def convert_key_value_to_ordered_dict(pairs: Optional[List[str]]) -> OrderedDict:
    """Convert a list of key-value pairs to an OrderedDict."""
    result = OrderedDict()
    if pairs is not None:
        for pair in pairs:
            key, value = pair.split("=")
            result[key] = int(value) if value.isdigit() else value
    return result


def flatten_ordered_dict(d: OrderedDict, parent_key: str = "", sep: str = "_") -> OrderedDict:
    """Flatten a nested OrderedDict."""
    items: List[Tuple[str, Union[str, int]]] = list()
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, OrderedDict):
            items.extend(flatten_ordered_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return OrderedDict(items)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", help="Output file path")
    args = parser.parse_args()

    # Determine input and output file paths
    input_file_path = args.input
    output_file_path = args.output

    # Prepare list of conntrack entries
    entries: List[OrderedDict] = list()

    # Parse the contents of the input file
    input_file = sys.stdin if input_file_path == "-" else open(input_file_path, 'r')
    with input_file:
        for line in input_file:
            # Split the line into parts
            parts = line.strip().split()

            # Extract protocol name and number
            proto_name, proto_num = parts[:2]
            del parts[:2]

            # Extract the optional timeout value
            timeout = str()
            if parts[0].isdigit():
                timeout = parts[0]
                del parts[0]
                
            # Extract the original and reply tuples
            torig = convert_key_value_to_ordered_dict(pop_next_tuple(parts))
            trepl = convert_key_value_to_ordered_dict(pop_next_tuple(parts))

            # Extract attributes and flags
            attrs = convert_key_value_to_ordered_dict(pop_all_attrs(parts))
            flags = convert_key_value_to_ordered_dict([f"{col.strip('[]').lower()}=1" for col in parts])

            # Construct the conntrack entry
            entry = OrderedDict([
                ('proto_name', proto_name), ('proto_num', proto_num), ('timeout', timeout),
                ('orig', torig), ('repl', trepl), *attrs.items(), *flags.items(),
            ])
            
            # Append the conntrack entry to the list
            entries.append(flatten_ordered_dict(entry))

    # Determine the fields of the conntrack entries
    fields = list(OrderedDict.fromkeys(key for item in entries for key in item.keys()))

    # Write the entries to the output CSV file
    output_file = sys.stdout if output_file_path == "-" else open(output_file_path, 'w', newline='')
    with output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(entries)
