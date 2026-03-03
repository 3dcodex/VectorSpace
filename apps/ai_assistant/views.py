from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message, AIAssistant

@login_required
def assistant_home(request):
    assistants = AIAssistant.objects.filter(active=True)
    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'ai_assistant/home.html', {
        'assistants': assistants,
        'conversations': conversations
    })

@login_required
def chat(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        conversation_id = request.POST.get('conversation_id')
        
        if conversation_id:
            conversation = get_object_or_404(Conversation, pk=conversation_id, user=request.user)
        else:
            conversation = Conversation.objects.create(
                user=request.user,
                title=content[:50]
            )
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=content
        )
        
        # Generate AI response (placeholder)
        ai_response = f"I understand you're asking about: {content}. This is a placeholder response. In production, this would connect to an AI API."
        
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )
        
        return redirect('ai_assistant:conversation', pk=conversation.pk)
    
    return render(request, 'ai_assistant/chat.html')

@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    messages = conversation.messages.all().order_by('created_at')
    
    return render(request, 'ai_assistant/conversation.html', {
        'conversation': conversation,
        'messages': messages
    })
