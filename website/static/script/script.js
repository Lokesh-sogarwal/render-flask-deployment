//// Simulating status updates
//let progress = 0;
//const progressElement = document.querySelector('.progress');
//const statusItems = document.querySelectorAll('.status-item');
//
//function updateStatus() {
//  if (progress < 100) {
//    progress += 25;
//    progressElement.style.width = `${progress}%`;
//
//    const activeIndex = progress / 25 - 1;
//    if (statusItems[activeIndex]) {
//      statusItems[activeIndex].classList.add('active');
//    }
//  }
//}
//
//// Simulate status update every 2 seconds
//setInterval(updateStatus, 2000);
