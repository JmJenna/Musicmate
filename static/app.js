const menuToggleBtn = document.querySelector('.navbar-toogleBtn');
const menuBars = document.querySelector('.nav-menu')

menuToggleBtn.addEventListener('click', ()=>{
  menuBars.classList.toggle('active');
})