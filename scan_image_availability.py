import csv
import json
from extract_student_image import extract_student_image_and_name
from collections import defaultdict

def scan_image_availability(csv_file='enrollments22.csv', output_file='image_availability_report.json'):
    """
    Scan CSV file to identify which batches/courses/colleges have images available.
    Tests the first enrollment number when course, college_id, or branch changes.
    """
    
    print("🔍 Starting image availability scan...\n")
    
    # Track unique combinations
    tested_combinations = set()
    results = {
        'with_images': [],
        'without_images': [],
        'summary': {}
    }
    
    # Track previous values to detect changes
    prev_course = None
    prev_college = None
    prev_branch = None
    prev_batch = None
    
    total_tested = 0
    with_images = 0
    without_images = 0
    
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for idx, row in enumerate(reader):
            enrollment = row['Enrollment Number'].strip()
            course = row['Course'].strip()
            batch = row['Batch'].strip()
            college_id = row['College ID'].strip()
            branch = row['Branch'].strip()
            
            # Create a unique key for this combination
            combo_key = f"{course}|{batch}|{college_id}|{branch}"
            
            # Check if any of the key fields changed or if this is the first row
            fields_changed = (
                course != prev_course or 
                college_id != prev_college or 
                branch != prev_branch or
                batch != prev_batch
            )
            
            # Test if this combination hasn't been tested yet and fields changed
            if combo_key not in tested_combinations and fields_changed:
                tested_combinations.add(combo_key)
                total_tested += 1
                
                print(f"[{total_tested}] Testing: {course.upper()} | Batch {batch} | College {college_id} | {branch}")
                print(f"    Enrollment: {enrollment}")
                
                # Try to extract image
                try:
                    image_url, name = extract_student_image_and_name(enrollment)
                    
                    combo_data = {
                        'course': course,
                        'batch': batch,
                        'college_id': college_id,
                        'branch': branch,
                        'enrollment_tested': enrollment,
                        'name': name
                    }
                    
                    if image_url:
                        print(f"    ✅ IMAGE FOUND: {name}")
                        combo_data['image_url'] = image_url
                        results['with_images'].append(combo_data)
                        with_images += 1
                    else:
                        print(f"    ❌ NO IMAGE AVAILABLE")
                        results['without_images'].append(combo_data)
                        without_images += 1
                        
                except Exception as e:
                    print(f"    ⚠️  ERROR: {e}")
                    results['without_images'].append({
                        'course': course,
                        'batch': batch,
                        'college_id': college_id,
                        'branch': branch,
                        'enrollment_tested': enrollment,
                        'error': str(e)
                    })
                    without_images += 1
                
                print()  # Empty line for readability
            
            # Update previous values
            prev_course = course
            prev_college = college_id
            prev_branch = branch
            prev_batch = batch
    
    # Generate summary
    results['summary'] = {
        'total_combinations_tested': total_tested,
        'with_images': with_images,
        'without_images': without_images,
        'success_rate': f"{(with_images/total_tested*100):.1f}%" if total_tested > 0 else "0%"
    }
    
    # Save results to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SCAN SUMMARY")
    print("="*60)
    print(f"Total combinations tested: {total_tested}")
    print(f"✅ With images: {with_images}")
    print(f"❌ Without images: {without_images}")
    print(f"Success rate: {results['summary']['success_rate']}")
    print(f"\n📄 Detailed report saved to: {output_file}")
    print("="*60)
    
    # Print batches without images
    if results['without_images']:
        print("\n⚠️  COMBINATIONS WITHOUT IMAGES:")
        print("-" * 60)
        for combo in results['without_images']:
            print(f"  • {combo['course'].upper()} | Batch {combo['batch']} | College {combo['college_id']} | {combo['branch']}")
        print("-" * 60)
    
    return results


def filter_csv_with_images(input_csv='enrollments22.csv', 
                           availability_report='image_availability_report.json',
                           output_csv='enrollments22_filtered.csv'):
    """
    Create a filtered CSV file containing only entries from combinations that have images.
    """
    
    print("\n🔧 Filtering CSV based on image availability...\n")
    
    # Load availability report
    with open(availability_report, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Create set of valid combinations (those with images)
    valid_combinations = set()
    for combo in report['with_images']:
        combo_key = f"{combo['course']}|{combo['batch']}|{combo['college_id']}|{combo['branch']}"
        valid_combinations.add(combo_key)
    
    print(f"Valid combinations with images: {len(valid_combinations)}")
    
    # Filter CSV
    kept_count = 0
    removed_count = 0
    
    with open(input_csv, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        with open(output_csv, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for row in reader:
                course = row['Course'].strip()
                batch = row['Batch'].strip()
                college_id = row['College ID'].strip()
                branch = row['Branch'].strip()
                
                combo_key = f"{course}|{batch}|{college_id}|{branch}"
                
                if combo_key in valid_combinations:
                    writer.writerow(row)
                    kept_count += 1
                else:
                    removed_count += 1
    
    print(f"✅ Kept: {kept_count} entries")
    print(f"❌ Removed: {removed_count} entries (no images)")
    print(f"📄 Filtered CSV saved to: {output_csv}")
    
    return kept_count, removed_count


if __name__ == "__main__":
    # Step 1: Scan for image availability
    print("="*60)
    print("STEP 1: SCANNING IMAGE AVAILABILITY")
    print("="*60 + "\n")
    
    results = scan_image_availability('enrollments22.csv', 'image_availability_report.json')
    
    # Step 2: Filter CSV to keep only entries with images
    print("\n" + "="*60)
    print("STEP 2: FILTERING CSV FILE")
    print("="*60 + "\n")
    
    filter_csv_with_images(
        input_csv='enrollments22.csv',
        availability_report='image_availability_report.json',
        output_csv='enrollments22_filtered.csv'
    )
    
    print("\n✨ Done! Use 'enrollments22_filtered.csv' for your scraping pipeline.")
