# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Contribution, Group, PayoutCycle
from .forms import ContributionForm

@login_required
def dashboard(request):
    user_groups = Group.objects.filter(members=request.user)
    contributions = Contribution.objects.filter(member=request.user)
    payout_cycles = PayoutCycle.objects.filter(group__in=user_groups).order_by('payout_date')
    
    context = {
        'groups': user_groups,
        'contributions': contributions,
        'payout_cycles': payout_cycles,
    }
    return render(request, 'contributions/dashboard.html', context)

@login_required
def contribute(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.member = request.user
            contribution.group = Group.objects.first()  # Assign the first group for simplicity
            contribution.save()
            return redirect('dashboard')
    else:
        form = ContributionForm()

    return render(request, 'contributions/contribute.html', {'form': form})

@login_required
def manage_cycle(request):
    user_groups = Group.objects.filter(members=request.user)
    next_payout = PayoutCycle.objects.filter(group__in=user_groups, status=False).first()
    
    if next_payout and next_payout.recipient == request.user:
        next_payout.status = True
        next_payout.save()
        # Handle payout logic and interest deduction
    
    return redirect('dashboard')