import csv
import json
from extract_student_image import extract_student_image_and_name
from collections import defaultdict
from datetime import datetime

def scan_image_availability(csv_file='enrollments22.csv', output_file='image_availability_report.json', log_file='image_avail.txt'):
    """
    Scan CSV file to identify which batches/courses/colleges have images available.
    Tests the first enrollment number when course, college_id, or branch changes.
    """
    
    # Open log file for writing
    log = open(log_file, 'w', encoding='utf-8')
    
    def log_print(message):
        """Print to console and write to log file"""
        print(message)
        log.write(message + '\n')
        log.flush()  # Ensure immediate write
    
    log_print("="*60)
    log_print(f"IMAGE AVAILABILITY SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_print("="*60)
    log_print("\n🔍 Starting image availability scan...\n")
    
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
                
                log_print(f"[{total_tested}] Testing: {course.upper()} | Batch {batch} | College {college_id} | {branch}")
                log_print(f"    Enrollment: {enrollment}")
                
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
                        log_print(f"    ✅ IMAGE FOUND: {name}")
                        log_print(f"    URL: {image_url}")
                        combo_data['image_url'] = image_url
                        results['with_images'].append(combo_data)
                        with_images += 1
                    else:
                        log_print(f"    ❌ NO IMAGE AVAILABLE")
                        results['without_images'].append(combo_data)
                        without_images += 1
                        
                except Exception as e:
                    log_print(f"    ⚠️  ERROR: {e}")
                    results['without_images'].append({
                        'course': course,
                        'batch': batch,
                        'college_id': college_id,
                        'branch': branch,
                        'enrollment_tested': enrollment,
                        'error': str(e)
                    })
                    without_images += 1
                
                log_print("")  # Empty line for readability
            
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
    log_print("\n" + "="*60)
    log_print("📊 SCAN SUMMARY")
    log_print("="*60)
    log_print(f"Total combinations tested: {total_tested}")
    log_print(f"✅ With images: {with_images}")
    log_print(f"❌ Without images: {without_images}")
    log_print(f"Success rate: {results['summary']['success_rate']}")
    log_print(f"\n📄 Detailed report saved to: {output_file}")
    log_print("="*60)
    
    # Print batches without images
    if results['without_images']:
        log_print("\n⚠️  COMBINATIONS WITHOUT IMAGES (WILL BE REMOVED):")
        log_print("-" * 60)
        for combo in results['without_images']:
            log_print(f"  • {combo['course'].upper()} | Batch {combo['batch']} | College {combo['college_id']} | {combo['branch']}")
        log_print("-" * 60)
    
    log.close()
    return results


def remove_entries_without_images(input_csv='enrollments22.csv', 
                                  availability_report='image_availability_report.json',
                                  backup_csv='enrollments22_backup.csv'):
    """
    Remove entries from enrollments22.csv that don't have images.
    Creates a backup before modifying.
    """
    
    print("\n🔧 Removing entries without images from CSV...\n")
    
    # Load availability report
    with open(availability_report, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Create set of valid combinations (those with images)
    valid_combinations = set()
    for combo in report['with_images']:
        combo_key = f"{combo['course']}|{combo['batch']}|{combo['college_id']}|{combo['branch']}"
        valid_combinations.add(combo_key)
    
    print(f"Valid combinations with images: {len(valid_combinations)}")
    
    # Create backup
    import shutil
    shutil.copy2(input_csv, backup_csv)
    print(f"✅ Backup created: {backup_csv}")
    
    # Read all rows
    rows_to_keep = []
    kept_count = 0
    removed_count = 0
    
    with open(input_csv, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        for row in reader:
            course = row['Course'].strip()
            batch = row['Batch'].strip()
            college_id = row['College ID'].strip()
            branch = row['Branch'].strip()
            
            combo_key = f"{course}|{batch}|{college_id}|{branch}"
            
            if combo_key in valid_combinations:
                rows_to_keep.append(row)
                kept_count += 1
            else:
                removed_count += 1
    
    # Overwrite original CSV with filtered data
    with open(input_csv, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_keep)
    
    print(f"\n✅ Kept: {kept_count} entries")
    print(f"❌ Removed: {removed_count} entries (no images)")
    print(f"📄 Updated CSV: {input_csv}")
    
    return kept_count, removed_count


if __name__ == "__main__":
    # Step 1: Scan for image availability
    print("="*60)
    print("STEP 1: SCANNING IMAGE AVAILABILITY")
    print("="*60 + "\n")
    
    results = scan_image_availability(
        csv_file='enrollments22.csv',
        output_file='image_availability_report.json',
        log_file='image_avail.txt'
    )
    
    # Step 2: Remove entries without images from the original CSV
    print("\n" + "="*60)
    print("STEP 2: REMOVING ENTRIES WITHOUT IMAGES")
    print("="*60 + "\n")
    
    remove_entries_without_images(
        input_csv='enrollments22.csv',
        availability_report='image_availability_report.json',
        backup_csv='enrollments22_backup.csv'
    )
    
    print("\n✨ Done!")
    print(f"📋 Logs saved to: image_avail.txt")
    print(f"📊 Report saved to: image_availability_report.json")
    print(f"💾 Backup saved to: enrollments22_backup.csv")
    print(f"✅ enrollments22.csv now contains only entries with images!")
