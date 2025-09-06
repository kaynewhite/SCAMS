import json
import sqlite3

def handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        # Get session from headers or query params
        session_data = get_session_from_request(event)
        if not session_data:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'success': False, 'message': 'Not authenticated'})
            }
        
        conn = sqlite3.connect('/tmp/clearance_system.db')
        cursor = conn.cursor()
        
        if event['httpMethod'] == 'POST':
            if session_data.get('user_type') != 'admin':
                return {
                    'statusCode': 403,
                    'headers': headers,
                    'body': json.dumps({'success': False, 'message': 'Admin access required'})
                }
            
            data = json.loads(event['body'])
            req_name = data.get('name', '').strip()
            
            if not req_name:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'success': False, 'message': 'Requirement name is required'})
                }
            
            try:
                cursor.execute('INSERT INTO requirements (name) VALUES (?)', (req_name,))
                conn.commit()
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({'success': True, 'message': 'Requirement added successfully'})
                }
            except sqlite3.IntegrityError:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'success': False, 'message': 'Requirement already exists'})
                }
            finally:
                conn.close()
        
        elif event['httpMethod'] == 'GET':
            cursor.execute('SELECT id, name FROM requirements ORDER BY name')
            requirements = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
            conn.close()
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(requirements)
            }
        
        elif event['httpMethod'] == 'DELETE':
            if session_data.get('user_type') != 'admin':
                return {
                    'statusCode': 403,
                    'headers': headers,
                    'body': json.dumps({'success': False, 'message': 'Admin access required'})
                }
            
            # Extract requirement ID from path
            path_parts = event['path'].split('/')
            req_id = int(path_parts[-1])
            
            # Delete associated student requirements first
            cursor.execute('DELETE FROM student_requirements WHERE requirement_id = ?', (req_id,))
            # Delete the requirement
            cursor.execute('DELETE FROM requirements WHERE id = ?', (req_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'success': True})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def get_session_from_request(event):
    # For simplicity, we'll use a header-based session
    # In production, you'd use JWT tokens or similar
    auth_header = event.get('headers', {}).get('authorization', '')
    if auth_header.startswith('Bearer '):
        try:
            session_data = json.loads(auth_header[7:])  # Remove 'Bearer '
            return session_data
        except:
            pass
    return None