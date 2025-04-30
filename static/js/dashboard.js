function loadConversations(conversations) {
let table = document.getElementById("conversationTable");
table.innerHTML = "";

conversations.forEach(conv => {
    let row = document.createElement("tr");
    // Extract phone number from contact info (format: "phone (city)")
    const phone = conv.contact.split(' ')[0];
    
    row.innerHTML = `
        <td>${conv.name}</td>
        <td>${conv.contact}</td>
        <td class="emotion-cell ${conv.emotionClass}">
            <span class="emotion-icon">${conv.emotion.split(' ')[0]}</span>
            <span class="emotion-text">${conv.emotion.split(' ')[1]}</span>
        </td>
        <td>${conv.summary}</td>
        <td>
            <a href="https://wa.me/${phone}" target="_blank" 
               class="btn btn-success btn-sm" 
               style="background: linear-gradient(45deg, #25D366, #128C7E);">
                <i class="fab fa-whatsapp"></i> WhatsApp
            </a>
        </td>
    `;
    table.appendChild(row);
});
}