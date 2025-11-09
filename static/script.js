/* Frontend chat + enhanced UI interactions */
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const addBtn = document.getElementById('addBtn');
const chatMessages = document.getElementById('chatMessages');
const orb = document.getElementById('orb');
const particleCanvas = document.getElementById('particleCanvas');
const typewriterEl = document.getElementById('typewriter');

// Chat session id (temporary)
let currentChatId = 'session_' + Date.now();

/* ------------------ Typewriter + header animation ------------------ */
const headerText = 'How can I help you today?';
function startTypewriter() {
    typewriterEl.textContent = '';
    const words = headerText.split(' ');
    let charIndex = 0;
    let wordIndex = 0;

    function typeChar() {
        if (charIndex < words[wordIndex].length) {
            typewriterEl.textContent += words[wordIndex][charIndex];
            charIndex++;
            setTimeout(typeChar, 45 + Math.random()*45);
        } else {
            // finish word, add space and small neon pulse
            typewriterEl.textContent += (wordIndex < words.length-1) ? ' ' : '';
            wordIndex++;
            charIndex = 0;
            pulseGlow();
            if (wordIndex < words.length) setTimeout(typeChar, 220);
        }
    }
    typeChar();
}

function pulseGlow(){
    const glow = document.querySelector('.glow-line');
    glow.animate([{ transform:'scaleX(0.6)', opacity:0.6 },{ transform:'scaleX(1)', opacity:1 },{ transform:'scaleX(0.9)', opacity:0.9 }], { duration:420, easing:'ease-out' });
}

/* ------------------ Particle system ------------------ */
let ctx, particles = [], cw, ch;
function initCanvas(){
    if(!particleCanvas) return;
    cw = particleCanvas.width = window.innerWidth;
    ch = particleCanvas.height = window.innerHeight;
    ctx = particleCanvas.getContext('2d');
    particleCanvas.style.width = '100%';
    particleCanvas.style.height = '100%';
    requestAnimationFrame(loopParticles);
}

function emit(x,y,amount=8){
    for(let i=0;i<amount;i++){
        particles.push({
            x:x, y:y,
            vx:(Math.random()-0.5)*2.2,
            vy:(Math.random()-0.9)*2.2 - 1,
            life:60 + Math.random()*40,
            r:1 + Math.random()*2,
            hue: 180 + Math.random()*140
        });
    }
}

function loopParticles(){
    if(!ctx) return;
    ctx.clearRect(0,0,cw,ch);
    for(let i=particles.length-1;i>=0;i--){
        const p = particles[i];
        p.x += p.vx; p.y += p.vy; p.vy += 0.02; p.life--;
        const alpha = Math.max(0, p.life/100);
        ctx.beginPath();
        ctx.fillStyle = `hsla(${p.hue},90%,60%,${alpha})`;
        ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fill();
        if(p.life<=0){ particles.splice(i,1); }
    }
    requestAnimationFrame(loopParticles);
}

function orbPosition(){
    const rect = orb.getBoundingClientRect();
    return { x: rect.left + rect.width/2, y: rect.top + rect.height/2 };
}

/* ------------------ Orb reactions ------------------ */
function orbPulse(){
    orb.classList.add('orb-listen');
    const core = orb.querySelector('.orb-core');
    core.classList.add('pulse');
    setTimeout(()=>{ orb.classList.remove('orb-listen'); core.classList.remove('pulse'); }, 420);
}

/* ------------------ Wire up input interactions ------------------ */
if(userInput){
    userInput.addEventListener('input', ()=>{
        // subtle orbit and particle emission while typing
        orbPulse();
        const pos = orbPosition();
        emit(pos.x + (Math.random()-0.5)*40, pos.y + (Math.random()-0.5)*40, 3);
    });

    userInput.addEventListener('focus', ()=>{ orb.classList.add('orb-listen'); });
    userInput.addEventListener('blur', ()=>{ orb.classList.remove('orb-listen'); });
}

window.addEventListener('resize', ()=>{ if(particleCanvas) initCanvas(); });

/* ------------------ Keep existing chat logic (simplified but preserved) ------------------ */
function generateChatId(){ return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2,9); }
currentChatId = generateChatId();

sendBtn && sendBtn.addEventListener('click', sendMessage);
userInput && userInput.addEventListener('keypress', (e)=>{ if(e.key==='Enter') sendMessage(); });
addBtn && addBtn.addEventListener('click', ()=>{ 
    currentChatId = generateChatId(); 
    chatMessages.innerHTML=''; 
    chatMessages.classList.remove('active'); 
});

async function saveMessageToDB(message,sender){
    try{ await fetch('/message',{ method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ chat_id: currentChatId, sender, message }) }); }catch(e){ console.warn('db save failed',e); }
}

async function sendMessage(){
    const message = userInput.value.trim(); 
    if(!message) return;
    
    chatMessages.classList.add('active'); 
    addMessageToChat(message,'user',true); 
    userInput.value=''; 
    orbPulse(); 
    const typing = showTypingIndicator();
    try{
        const res = await fetch('/chat',{ method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ message }) });
        const data = await res.json(); 
        removeTypingIndicator(typing);
        if(data.status==='success') addMessageToChat(data.response,'bot',true); 
        else addMessageToChat('Sorry, something went wrong.','bot',true);
    }catch(e){ 
        removeTypingIndicator(typing); 
        addMessageToChat('Sorry, I couldn\'t reach server.','bot',true); 
    }
}

function addMessageToChat(message,sender,saveToDb=false){
    const messageDiv = document.createElement('div'); 
    messageDiv.classList.add('message'); 
    messageDiv.textContent = message; 
    if(sender==='user') messageDiv.classList.add('user-message'); 
    else messageDiv.classList.add('bot-message');
    chatMessages.appendChild(messageDiv); 
    // Smooth scroll to bottom
    setTimeout(()=>{
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
    if(saveToDb) saveMessageToDB(message,sender);
}

function showTypingIndicator(){ 
    const d = document.createElement('div'); 
    d.className='typing-indicator'; 
    d.innerHTML='<span></span><span></span><span></span>'; 
    chatMessages.appendChild(d); 
    setTimeout(()=>{
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
    return d; 
}
function removeTypingIndicator(ind){ if(ind && ind.parentNode) ind.parentNode.removeChild(ind); }

/* ------------------ Init on DOM ready ------------------ */
window.addEventListener('DOMContentLoaded', ()=>{ 
    startTypewriter(); 
    initCanvas(); 
    // kick tiny intro particles
    setTimeout(()=>{ const p = orbPosition(); emit(p.x,p.y,18); }, 700);
});

