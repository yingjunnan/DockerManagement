from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import docker
import requests
import json
import time

app = Flask(__name__)
CORS(app)

client = docker.from_env()

# 存储拉取任务的状态
pull_tasks = {}

@app.route('/api/images', methods=['GET'])
def list_images():
    try:
        images = client.images.list()
        return jsonify([{
            'Id': image.id,
            'RepoTags': image.tags,
            'Size': image.attrs['Size']
        } for image in images])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/images/search', methods=['GET'])
def search_images():
    try:
        term = request.args.get('term', '')
        results = client.images.search(term)
        formatted_results = [{
            'name': item['name'],
            'description': item['description'],
            'stars': item.get('star_count', 0),
            'official': item.get('is_official', False),
            'automated': item.get('is_automated', False)
        } for item in results]
        return jsonify(formatted_results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/images/pull', methods=['POST'])
def pull_image():
    try:
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Image name is required'}), 400

        # 生成任务ID
        task_id = str(time.time())
        pull_tasks[task_id] = {
            'id': task_id,
            'status': 'pending',
            'progress': 0,
            'message': '准备拉取镜像...',
            'image': name
        }

        def do_pull():
            try:
                layers_progress = {}
                
                for line in client.api.pull(name, stream=True, decode=True):
                    if task_id not in pull_tasks:
                        break
                        
                    status = line.get('status', '')
                    progress_detail = line.get('progressDetail', {})
                    id = line.get('id', '')
                    
                    if status == 'Downloading':
                        if id and progress_detail:
                            current = progress_detail.get('current', 0)
                            total = progress_detail.get('total', 0)
                            if total > 0:
                                layers_progress[id] = (current / total) * 100
                                
                            # 计算总体进度
                            if layers_progress:
                                total_progress = sum(layers_progress.values()) / len(layers_progress)
                                pull_tasks[task_id].update({
                                    'status': 'downloading',
                                    'progress': round(total_progress, 1),
                                    'message': f'正在下载层 {id}: {round(current/total*100, 1)}%'
                                })
                    
                    elif status == 'Download complete':
                        if id in layers_progress:
                            layers_progress[id] = 100
                    
                    elif status == 'Pull complete':
                        pull_tasks[task_id].update({
                            'status': 'extracting',
                            'message': f'正在解压层 {id}'
                        })
                
                # 拉取完成
                pull_tasks[task_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'message': '拉取完成'
                })
                
            except Exception as e:
                if task_id in pull_tasks:
                    pull_tasks[task_id].update({
                        'status': 'failed',
                        'message': str(e)
                    })

        # 启动后台任务
        from threading import Thread
        thread = Thread(target=do_pull)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': 'Pull task started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/images/pull/progress/<task_id>', methods=['GET'])
def get_pull_progress(task_id):
    def generate():
        try:
            while True:
                # 检查任务是否存在
                if task_id not in pull_tasks:
                    yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                    break

                task = pull_tasks[task_id]
                status = task['status']
                
                # 如果任务完成或失败，发送最终状态并结束
                if status in ['completed', 'failed']:
                    yield f"data: {json.dumps(task)}\n\n"
                    break
                
                # 发送当前进度
                yield f"data: {json.dumps(task)}\n\n"
                time.sleep(0.5)  # 控制更新频率
                
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        # 清理完成的任务
        if task_id in pull_tasks:
            del pull_tasks[task_id]
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/images/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    try:
        client = docker.from_env()
        # 获取镜像信息
        image = None
        try:
            image = client.images.get(image_id)
        except docker.errors.ImageNotFound:
            return jsonify({'error': '镜像不存在'}), 404
            
        # 如果镜像有多个标签，需要先删除所有标签
        if image.tags:
            for tag in image.tags:
                try:
                    client.images.remove(tag, force=False)
                except docker.errors.APIError:
                    # 如果删除标签失败，继续尝试下一个
                    continue
                    
        # 最后尝试删除镜像本身
        try:
            client.images.remove(image_id, force=True)
        except docker.errors.APIError as e:
            if 'image is being used by running container' in str(e):
                return jsonify({'error': '无法删除：镜像正在被容器使用'}), 400
            return jsonify({'error': f'删除失败：{str(e)}'}), 400
            
        return jsonify({'message': '镜像删除成功'})
        
    except Exception as e:
        app.logger.error(f'删除镜像时发生错误: {str(e)}')
        return jsonify({'error': f'删除失败：{str(e)}'}), 400

@app.route('/api/images/tags', methods=['GET'])
def get_image_tags():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({'error': 'Image name is required'}), 400
            
        # 使用Docker Hub API获取镜像信息
        namespace = 'library' if '/' not in name else name.split('/')[0]
        repo_name = name.split('/')[-1]
        
        # 构建API URL
        if namespace == 'library':
            url = f'https://hub.docker.com/v2/repositories/library/{repo_name}/tags'
        else:
            url = f'https://hub.docker.com/v2/repositories/{namespace}/{repo_name}/tags'
            
        response = requests.get(url, params={'page_size': 100})
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch tags'}), 500
            
        data = response.json()
        tags = []
        
        for item in data.get('results', []):
            images = item.get('images', [])
            if not images:
                continue
                
            architectures = []
            for img in images:
                arch = img.get('architecture')
                if arch and arch not in architectures:
                    architectures.append(arch)
            
            tag_info = {
                'name': item['name'],
                'full_size': item.get('full_size', 0),
                'last_updated': item.get('last_updated', ''),
                'architectures': architectures,
                'os': images[0].get('os', 'linux')
            }
            tags.append(tag_info)
            
        return jsonify(tags)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/images/save/<path:image_name>')
def save_image(image_name):
    try:
        # 获取 Docker 客户端
        client = docker.from_env()
        
        # 获取镜像
        image = client.images.get(image_name)
        
        # 创建响应对象，使用生成器流式传输数据
        def generate():
            for chunk in image.save(chunk_size=2097152):  # 2MB chunks
                yield chunk
        
        response = Response(generate(), mimetype='application/x-tar')
        response.headers['Content-Disposition'] = f'attachment; filename={image_name.replace("/", "-")}.tar'
        return response
        
    except docker.errors.ImageNotFound:
        return jsonify({'error': f'镜像 {image_name} 未找到'}), 404
    except docker.errors.APIError as e:
        return jsonify({'error': f'Docker API 错误: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'保存镜像时发生错误: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
