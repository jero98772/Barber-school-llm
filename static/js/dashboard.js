function loadConversations(conversations) {
    let table = document.getElementById("conversationTable");
    table.innerHTML = "";

    conversations.forEach(conv => {
        let row = document.createElement("tr");
        row.innerHTML = `
            <td>${conv.name}</td>
            <td>${conv.contact}</td>
            <td class="${conv.emotionClass}">${conv.emotion}</td>
            <td>${conv.summary}</td>
            <td><a href="whatsapp"><button class="contact-btn">Contact</button></a></td>
        `;
        table.appendChild(row);
    });
}

