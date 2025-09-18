#!/usr/bin/env python3
"""
Format MPD (Mean Preference Difference) results from text file to JSON format.
This script parses MPD results and extracts audio path, human annotation, 
and model hypothesis for each record.
"""

import json
import re
import argparse
from pathlib import Path


def parse_mpd_file(input_file):
    """
    Parse the MPD text file and extract records.
    
    Args:
        input_file (str): Path to the input MPD text file
        
    Returns:
        list: List of parsed records with audio path, human annotation, and hypothesis
    """
    records = []
    current_record = {}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    # Skip header lines until we reach the first audio file path
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('/') and line.endswith('.wav'):
            break
        i += 1
    
    # Parse records
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is an audio file path
        if line.startswith('/') and line.endswith('.wav'):
            # If we have a previous record, save it
            if current_record:
                records.append(current_record)
            
            # Start new record
            current_record = {
                'audio_path': line,
                'human_annotation': {},
                'model_prediction': {},
                'statistics': {}
            }
            
        elif line == "Human annotation: Canonical vs Perceived:":
            # Parse human annotation
            if i + 3 < len(lines):
                canonical_line = lines[i + 1].strip()
                comparison_line = lines[i + 2].strip()
                perceived_line = lines[i + 3].strip()
                
                current_record['human_annotation'] = {
                    'canonical': parse_phoneme_sequence(canonical_line),
                    'comparison': parse_phoneme_sequence(comparison_line),
                    'perceived': parse_phoneme_sequence(perceived_line)
                }
                i += 3
                
        elif line == "Model Prediction: Canonical vs Hypothesis:":
            # Parse model prediction
            if i + 3 < len(lines):
                canonical_line = lines[i + 1].strip()
                comparison_line = lines[i + 2].strip()
                hypothesis_line = lines[i + 3].strip()
                
                current_record['model_prediction'] = {
                    'canonical': parse_phoneme_sequence(canonical_line),
                    'comparison': parse_phoneme_sequence(comparison_line),
                    'hypothesis': parse_phoneme_sequence(hypothesis_line)
                }
                i += 3
                
        elif line.startswith("True Accept:"):
            # Parse statistics
            stats_match = re.match(
                r'True Accept: (\d+), False Rejection: (\d+), False Accept: (\d+), '
                r'True Reject: (\d+), Corr(?:ect)? Diag: (\d+), Err(?:or)? Diag: (\d+)',
                line
            )
            if stats_match:
                current_record['statistics'] = {
                    'true_accept': int(stats_match.group(1)),
                    'false_rejection': int(stats_match.group(2)),
                    'false_accept': int(stats_match.group(3)),
                    'true_reject': int(stats_match.group(4)),
                    'correct_diag': int(stats_match.group(5)),
                    'error_diag': int(stats_match.group(6))
                }
        
        i += 1
    
    # Add the last record if it exists
    if current_record:
        records.append(current_record)
    
    return records


def parse_phoneme_sequence(line):
    """
    Parse a phoneme sequence line and return as a list.
    
    Args:
        line (str): Line containing phonemes separated by semicolons
        
    Returns:
        list: List of phonemes
    """
    if not line:
        return []
    
    # Split by semicolon and clean up whitespace
    phonemes = [phoneme.strip() for phoneme in line.split(';')]
    
    # Remove empty strings and handle special tokens
    phonemes = [p for p in phonemes if p]
    
    return phonemes


def save_to_json(records, output_file, indent=2):
    """
    Save records to JSON file.
    
    Args:
        records (list): List of parsed records
        output_file (str): Path to output JSON file
        indent (int): JSON indentation level
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_records': len(records),
            'records': records
        }, f, ensure_ascii=False, indent=indent)
    
    print(f"Successfully converted {len(records)} records to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert MPD results from text format to JSON format"
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help="Input MPD text file path"
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help="Output JSON file path"
    )
    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help="JSON indentation level (default: 2)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' does not exist")
        return 1
    
    try:
        # Parse the MPD file
        print(f"Parsing MPD file: {args.input}")
        records = parse_mpd_file(args.input)
        
        if not records:
            print("Warning: No valid records found in the input file")
            return 1
        
        # Save to JSON
        save_to_json(records, args.output, args.indent)
        
        # Print summary
        print(f"\nSummary:")
        print(f"- Total records processed: {len(records)}")
        print(f"- Output file: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())