// 预约相关的JavaScript代码
document.addEventListener('DOMContentLoaded', function() {
    const departmentSelect = document.getElementById('department');
    const doctorSelect = document.getElementById('doctor');
    const dateInput = document.getElementById('date');
    const timeSelect = document.getElementById('time');
    const doctorInfo = document.getElementById('doctorInfo');
    
    // 科室选择变化时更新医生列表
    departmentSelect.addEventListener('change', function() {
        const department = this.value;
        console.log('选择科室:', department);
        
        doctorSelect.disabled = true;
        doctorSelect.innerHTML = '<option value="">请选择医生</option>';
        timeSelect.disabled = true;
        timeSelect.innerHTML = '<option value="">请先选择日期</option>';
        doctorInfo.innerHTML = '<p class="text-muted">请选择医生查看详细信息</p>';
        
        if (department) {
            fetch(`/api/doctors?department=${encodeURIComponent(department)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('获取医生列表失败');
                    }
                    return response.json();
                })
                .then(doctors => {
                    console.log('获取到的医生列表:', doctors);
                    doctors.forEach(doctor => {
                        const option = document.createElement('option');
                        option.value = doctor.id;
                        option.textContent = doctor.name;
                        doctorSelect.appendChild(option);
                    });
                    doctorSelect.disabled = false;
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('获取医生列表失败，请稍后重试', 'danger');
                });
        }
    });
    
    // 医生选择变化时更新医生信息
    doctorSelect.addEventListener('change', function() {
        const doctorId = this.value;
        console.log('选择医生:', doctorId);
        
        if (doctorId) {
            fetch(`/api/doctor/${doctorId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('获取医生信息失败');
                    }
                    return response.json();
                })
                .then(doctor => {
                    console.log('获取到的医生信息:', doctor);
                    doctorInfo.innerHTML = `
                        <p><strong>姓名：</strong>${doctor.name}</p>
                        <p><strong>科室：</strong>${doctor.department}</p>
                        <p><strong>专业：</strong>${doctor.specialty}</p>
                    `;
                    // 如果已经选择了日期，重新获取可用时间
                    if (dateInput.value) {
                        updateAvailableTimes();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('获取医生信息失败，请稍后重试', 'danger');
                });
        } else {
            doctorInfo.innerHTML = '<p class="text-muted">请选择医生查看详细信息</p>';
        }
    });
    
    // 更新可用时间的函数
    function updateAvailableTimes() {
        const doctorId = doctorSelect.value;
        const date = dateInput.value;
        console.log('更新可用时间 - 医生:', doctorId, '日期:', date);
        
        timeSelect.disabled = true;
        timeSelect.innerHTML = '<option value="">请选择时间</option>';
        
        if (date && doctorId) {
            fetch(`/api/available_times?doctor_id=${doctorId}&date=${date}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('获取可用时间失败');
                    }
                    return response.json();
                })
                .then(times => {
                    console.log('获取到的可用时间:', times);
                    if (times.length === 0) {
                        const option = document.createElement('option');
                        option.value = "";
                        option.textContent = "该日期无可用时间";
                        timeSelect.appendChild(option);
                    } else {
                        times.forEach(time => {
                            const option = document.createElement('option');
                            option.value = time;
                            option.textContent = time;
                            timeSelect.appendChild(option);
                        });
                        timeSelect.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('获取可用时间失败，请稍后重试', 'danger');
                });
        }
    }
    
    // 日期选择变化时更新可用时间段
    dateInput.addEventListener('change', updateAvailableTimes);
    
    // 表单提交前验证
    document.getElementById('appointmentForm').addEventListener('submit', function(e) {
        if (!departmentSelect.value || !doctorSelect.value || !dateInput.value || !timeSelect.value) {
            e.preventDefault();
            showMessage('请填写所有必要信息', 'warning');
        }
    });
}); 