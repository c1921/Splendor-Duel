document.addEventListener('DOMContentLoaded', () => {
    // 获取所有格子
    const cells = document.querySelectorAll('.cell');
    const resetButton = document.getElementById('reset-button');
    
    // 为每个格子添加点击事件
    cells.forEach(cell => {
        cell.addEventListener('click', handleCellClick);
    });
    
    // 重置按钮事件
    resetButton.addEventListener('click', resetGame);
    
    // 格子点击处理函数
    async function handleCellClick(event) {
        const cell = event.currentTarget;
        
        // 如果格子已经是空的，则不做任何操作
        if (cell.classList.contains('empty')) {
            return;
        }
        
        const row = cell.getAttribute('data-row');
        const col = cell.getAttribute('data-col');
        
        try {
            // 创建表单数据
            const formData = new FormData();
            formData.append('row', row);
            formData.append('col', col);
            
            // 发送移动请求
            const response = await fetch('/api/move', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('移动请求失败');
            }
            
            const data = await response.json();
            
            // 更新UI
            updateUI(data);
            
        } catch (error) {
            console.error('错误:', error);
            alert('操作失败：' + error.message);
        }
    }
    
    // 重置游戏函数
    async function resetGame() {
        try {
            const response = await fetch('/api/reset', {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('重置请求失败');
            }
            
            const data = await response.json();
            
            // 更新UI
            updateUI(data);
            
        } catch (error) {
            console.error('错误:', error);
            alert('重置失败：' + error.message);
        }
    }
    
    // 更新UI函数
    function updateUI(data) {
        const { grid, collection_area } = data;
        
        // 更新格子
        cells.forEach(cell => {
            const row = parseInt(cell.getAttribute('data-row'));
            const col = parseInt(cell.getAttribute('data-col'));
            
            // 获取当前格子对应的数据
            const cellData = grid[row][col];
            
            // 清空格子内容
            cell.innerHTML = '';
            
            // 更新格子样式和内容
            if (cellData.token) {
                cell.classList.remove('empty');
                const tokenElement = document.createElement('div');
                tokenElement.className = 'token';
                cell.appendChild(tokenElement);
            } else {
                cell.classList.add('empty');
            }
        });
        
        // 更新收集区
        const collectionContainer = document.querySelector('.collected-tokens');
        collectionContainer.innerHTML = '';
        
        collection_area.forEach(tokenId => {
            const tokenElement = document.createElement('div');
            tokenElement.className = 'token collected';
            tokenElement.setAttribute('data-id', tokenId);
            collectionContainer.appendChild(tokenElement);
        });
    }
}); 