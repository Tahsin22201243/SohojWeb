// small theme JS: reveal animations & subtle interactions
document.addEventListener('DOMContentLoaded', function(){
    // reveal elements with .fade-up when they enter viewport
    const toReveal = document.querySelectorAll('.fade-up');
    const io = new IntersectionObserver((entries)=>{
        entries.forEach(e=>{
            if(e.isIntersecting){
                e.target.classList.add('in');
                io.unobserve(e.target);
            }
        })
    }, {threshold: 0.15});
    toReveal.forEach(el=>io.observe(el));

    // small ripple effect on brand buttons
    document.querySelectorAll('.btn-brand').forEach(btn=>{
        btn.addEventListener('mouseenter', ()=> btn.style.transform='translateY(-3px)');
        btn.addEventListener('mouseleave', ()=> btn.style.transform='translateY(0)');
    });

    // animated progress bars (animate width to data-target when visible)
    const progressBars = document.querySelectorAll('.animated-progress');
    const pbObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if(entry.isIntersecting){
                const el = entry.target;
                const target = parseFloat(el.getAttribute('data-target') || '0');
                // simple animation
                let current = 0;
                const step = Math.max(1, Math.ceil(target / 20));
                const interval = setInterval(()=>{
                    current = Math.min(target, current + step);
                    el.style.width = current + '%';
                    el.setAttribute('aria-valuenow', current);
                    if(current >= target) clearInterval(interval);
                }, 12);
                pbObserver.unobserve(el);
            }
        })
    }, {threshold: 0.1});
    progressBars.forEach(p=>pbObserver.observe(p));

    // subtle pulse highlight for funded cards
    document.querySelectorAll('.funded-card').forEach(card=>{
        card.classList.add('funded-ready');
        setTimeout(()=> card.classList.add('funded-pulse'), 700);
    });
});
