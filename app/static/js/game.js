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
            if (cellData.has_gem && cellData.gem) {
                cell.classList.remove('empty');
                const gemElement = document.createElement('div');
                gemElement.className = `gem type-${cellData.gem.type}`;
                gemElement.textContent = cellData.gem.type;
                cell.appendChild(gemElement);
            } else {
                cell.classList.add('empty');
            }
        });
        
        // 更新收集区
        const collectionContainer = document.querySelector('.collected-gems');
        collectionContainer.innerHTML = '';
        
        // 创建宝石计数对象
        const gemCounts = {
            'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'α': 0, 'β': 0
        };
        
        // 添加收集的宝石
        collection_area.forEach(gem => {
            const gemElement = document.createElement('div');
            gemElement.className = `gem type-${gem.type}`;
            gemElement.setAttribute('data-id', gem.id);
            gemElement.textContent = gem.type;
            collectionContainer.appendChild(gemElement);
            
            // 增加宝石计数
            gemCounts[gem.type]++;
        });
        
        // 更新宝石统计
        const gemCountList = document.querySelector('.gem-count-list');
        if (gemCountList) {
            gemCountList.innerHTML = '';
            
            for (const [type, count] of Object.entries(gemCounts)) {
                const countItem = document.createElement('div');
                countItem.className = 'gem-count-item';
                
                const colorDiv = document.createElement('div');
                colorDiv.className = `gem-count-color ${type}`;
                
                const countSpan = document.createElement('span');
                countSpan.textContent = `${type}: ${count}`;
                
                countItem.appendChild(colorDiv);
                countItem.appendChild(countSpan);
                gemCountList.appendChild(countItem);
            }
        }
    }
}); 