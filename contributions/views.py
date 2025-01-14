# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Group, PayoutCycle, Contribution
from .forms import GroupForm, ContributionForm, MemberManagementForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import messages
import uuid
from django.db.models import Sum
from django.db import models
from datetime import timedelta
from django.utils.timezone import now, timedelta




@login_required
def dashboard(request):
    groups = Group.objects.filter(members=request.user)
    # contributions = Contribution.objects.filter(group__in=groups)
    
    # # Calculate total balance for each group
    # group_balances = contributions.values('group').annotate(total_amount=Sum('amount'))

    # # Fetch the next payout cycle for each group
    # next_payouts = PayoutCycle.objects.filter(group__in=groups, status=False).order_by('payout_date')
    # group_form = GroupForm()

    # if request.method == 'POST':
        
    #  if 'name' in request.POST:  # Group creation
    #     group_form = GroupForm(request.POST)
    #     if group_form.is_valid():
    #         group = group_form.save(commit=False)  # Prevent immediate save
    #         group.admin = request.user  # Set admin to current user
    #         group.save()  # Now save the group
    #         group.members.add(request.user)  # Add creator as member
    #         messages.success(request, 'Group created successfully.')
    #         return redirect('dashboard')
    #     elif 'group_code' in request.POST:  # Joining a group
    #         group_id = request.POST.get('group_code')
    #         group = get_object_or_404(Group, id=group_id)
    #         group.members.add(request.user)
    #         messages.success(request, 'Successfully joined the group.')
    #         return redirect('dashboard')

    return render(request, 'contributions/dashboard.html', {
        'groups': groups,
        # 'group_form': group_form,
        # 'group_balances': group_balances,
        # 'next_payouts': next_payouts
    })
    
    
@login_required
def contribute(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        amount = request.POST.get('amount')
        
        group = get_object_or_404(Group, id=group_id)
        
        if amount and float(amount) > 0:
            contribution = Contribution(
                member=request.user,
                group=group,
                amount=amount
            )
            contribution.save()
            messages.success(request, f"You contributed KES {amount} to {group.name}.")
        else:
            messages.error(request, "Invalid amount entered.")

    return redirect('dashboard')


@login_required
def manage_cycle(request):
    user_groups = Group.objects.filter(members=request.user)
    next_payout = PayoutCycle.objects.filter(group__in=user_groups, status=False).first()
    
    if next_payout and next_payout.recipient == request.user:
        next_payout.status = True
        next_payout.save()
        # Handle payout logic and interest deduction
    
    return redirect('dashboard')

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    contributions = Contribution.objects.filter(group=group).order_by('-contribution_date')

    if request.user not in group.members.all():
        messages.error(request, "You are not authorized to view this group.")
        return redirect('dashboard')
    
    
    contributions = group.contribution_set.all()  # Fetch all contributions for this group
    total_balance = contributions.aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Calculate total balance for each group
    group_balances = contributions.values('group').annotate(total_amount=Sum('amount'))



    form = MemberManagementForm()

    if request.method == 'POST':
        if 'generate_code' in request.POST:
            group.generate_join_code()
            messages.success(request, f"Join code generated: {group.join_code}")
        elif 'manage_member' in request.POST:
            form = MemberManagementForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                action = form.cleaned_data['action']
                if action == 'add':
                    group.members.add(user)
                    messages.success(request, f"{user.username} added to the group.")
                elif action == 'remove':
                    if user == group.admin:
                        messages.error(request, "Admin cannot be removed from the group.")
                    else:
                        group.members.remove(user)
                        messages.success(request, f"{user.username} removed from the group.")
        return redirect('group_detail', group_id=group.id)
    
    
     # Calculate next payout
    members = group.members.all().order_by('username')  # Alphabetical order
    total_balance = group.contribution_set.aggregate(total=models.Sum('amount'))['total'] or 0
    cycle_length = group.payoutcycle_set.count()

    # Find the next member to receive payout
    next_member_index = cycle_length % members.count()  # Circular index
    next_member = members[next_member_index]
    next_payout_date = (now() + timedelta(days=(6 - now().weekday()))).replace(hour=8, minute=0, second=0, microsecond=0)

    return render(request, 'contributions/group_detail.html', {
        'group': group,
        'form': form,
        'contributions': contributions,
        'total_balance': total_balance,
        'group_balances': group_balances,
        'next_member': next_member,
        'next_payout_date': next_payout_date,
        'created_at': group.created_at,
    })


#   contributions = group.contribution_set.all()
#  'contributions': contributions



@login_required
def join_group(request):
    if request.method == 'POST':
        join_code = request.POST.get('group_code')
        try:
            group = Group.objects.get(join_code=join_code)
            if request.user in group.members.all():
                messages.info(request, "You are already a member of this group.")
            else:
                group.members.add(request.user)
                messages.success(request, f"You have successfully joined {group.name}.")
        except Group.DoesNotExist:
            messages.error(request, "Invalid join code. Please try again.")
        return redirect('dashboard')
    else:
        return render(request, 'contributions/join_group.html')  # Ensure this template exists

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user  # Automatically set the user as admin
            group.save()
            group.add_member(request.user)  # Add the creator as a member
            messages.success(request, 'Group created successfully!')
            return redirect('dashboard')
    else:
        form = GroupForm()
    return render(request, 'contributions/create_group.html', {'form': form})

@login_required
def generate_join_code(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user == group.admin:
        group.join_code = str(uuid.uuid4())[:8]
        group.save()
        messages.success(request, f'Join code generated: {group.join_code}')
    else:
        messages.error(request, 'You are not authorized to generate a join code.')
    return redirect('group_detail', group_id=group.id)


#contribution history view
@login_required
def contribution_history(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.members.all():
        messages.error(request, "You are not authorized to view this group's history.")
        return redirect('dashboard')

    contributions = group.contribution_set.all().order_by('-contribution_date')  # Order by most recent

    return render(request, 'contributions/history.html', {
        'group': group,
        'contributions': contributions,
    })
    
    
@login_required    
def help_page(request):
    return render(request, 'contributions/help.html')