# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib import messages
# from django.db import transaction
# from .models import ClearFee, UploadFee
# from student.models import Student, Batch, Semester, Section, Discipline
# from django.utils import timezone
# from datetime import datetime, date
# from decimal import Decimal, InvalidOperation
# from django.db.models import Sum
# from .models import UploadFee, ClearFee
# from student.models import Student


# def upload_fee(request):
#     batches = Batch.objects.all()
#     semesters = Semester.objects.all()
#     sections = Section.objects.all()
#     disciplines = Discipline.objects.all()

#     students = None

#     if request.method == "POST":
#         discipline_id = request.POST.get("discipline")
#         batch_id = request.POST.get("batch")
#         section_id = request.POST.get("section")
#         semester_id = request.POST.get("semester")
#         semester_option = request.POST.get("semester_option")

#         amount_default = request.POST.get("amount")
#         due_date_str = request.POST.get("due_date")
#         fine_amount = request.POST.get("fine_amount", "5000")  # Default fine amount

#         if due_date_str:
#             try:
#                 due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
#             except:
#                 due_date = date.today()
#         else:
#             due_date = date.today()

#         if "load_students" in request.POST:
#             students = Student.objects.filter(
#                 batch_id=batch_id,
#                 semester_id=semester_id,
#                 section_id=section_id,
#                 discipline_id=discipline_id
#             )

#         if "submit_all" in request.POST:
#             students = Student.objects.filter(
#                 batch_id=batch_id,
#                 semester_id=semester_id,
#                 section_id=section_id,
#                 discipline_id=discipline_id
#             )

#             today = date.today()
            
#             # Convert fine amount to Decimal with proper handling
#             try:
#                 auto_fine = Decimal(fine_amount) if fine_amount else Decimal('5000')
#             except (InvalidOperation, ValueError, TypeError):
#                 auto_fine = Decimal('5000')

#             with transaction.atomic():
#                 for st in students:
#                     # Get individual student amount from the form
#                     # The form has inputs like base_amount_{st.id} and total_amount_{st.id}
#                     base_amount_str = request.POST.get(f"base_amount_{st.id}", amount_default)
#                     fine_amount_str = request.POST.get(f"fine_amount_{st.id}", fine_amount)
                    
#                     # Convert to Decimal with proper error handling
#                     try:
#                         amount = Decimal(base_amount_str) if base_amount_str and base_amount_str.strip() else Decimal('0')
#                     except (InvalidOperation, ValueError, TypeError):
#                         amount = Decimal('0')
                        
#                     try:
#                         student_fine = Decimal(fine_amount_str) if fine_amount_str and fine_amount_str.strip() else auto_fine
#                     except (InvalidOperation, ValueError, TypeError):
#                         student_fine = auto_fine
                    
#                     # Ensure amount is not None and not negative
#                     if amount is None or amount < 0:
#                         amount = Decimal('0')
                    
#                     # Add automatic fine if past due date
#                     final_fine = student_fine
#                     if today > due_date:
#                         final_fine += Decimal('100')  # Additional late fine

#                     UploadFee.objects.update_or_create(
#                         student=st,
#                         semester_option=semester_option,
#                         defaults={
#                             "batch_id": batch_id,
#                             "semester_id": semester_id,
#                             "section_id": section_id,
#                             "discipline_id": discipline_id,
#                             "amount": amount,  # This should now be a Decimal, not None
#                             "fine": final_fine,
#                             "due_date": due_date
#                         }
#                     )

#             messages.success(request, "Fees uploaded successfully.")
#             return redirect("fee_list")

#     return render(
#         request,
#         "fees/upload_fee.html",  # Changed path to match your template
#         {
#             "batches": batches,
#             "semesters": semesters,
#             "sections": sections,
#             "disciplines": disciplines,
#             "students": students,
#         }
#     )

# def fee_list(request):
#     batches = Batch.objects.all()
#     semesters = Semester.objects.all()
#     disciplines = Discipline.objects.all()

#     batch_filter = request.GET.get("batch")
#     semester_filter = request.GET.get("semester")
#     section_filter = request.GET.get("section")
#     discipline_filter = request.GET.get("discipline")

#     all_sections = Section.objects.select_related('batch').all()
#     all_batches = Batch.objects.select_related('discipline').all()

#     fees = UploadFee.objects.select_related(
#         "student", "batch", "semester", "section", "discipline"
#     )

#     if batch_filter:
#         fees = fees.filter(batch_id=batch_filter)
#     if semester_filter:
#         fees = fees.filter(semester_id=semester_filter)
#     if section_filter:
#         fees = fees.filter(section_id=section_filter)
#     if discipline_filter:
#         fees = fees.filter(discipline_id=discipline_filter)

#     student_fees = {}
#     for fee in fees:
#         student_id = fee.student.id
#         if student_id not in student_fees:
#             student_fees[student_id] = {
#                 'student': fee.student,
#                 'batch': fee.batch,
#                 'semester': fee.semester,
#                 'section': fee.section,
#                 'fees': [],
#                 'total_all': 0,  # Total of all fees
#                 'total_pending': 0,  # Total of pending fees only
#                 'total_cleared': 0,  # Total of cleared fees only
#             }
        
#         # Add clearance status to each fee
#         fee.is_cleared = ClearFee.objects.filter(upload_fee=fee).exists()
#         student_fees[student_id]['fees'].append(fee)
        
#         # Add to total_all (all fees)
#         student_fees[student_id]['total_all'] += fee.total_fee()
        
#         # Add to appropriate total based on clearance status
#         if fee.is_cleared:
#             student_fees[student_id]['total_cleared'] += fee.total_fee()
#         else:
#             student_fees[student_id]['total_pending'] += fee.total_fee()

#     selected_batch_name = ""
#     selected_section_name = ""
#     selected_discipline_name = ""
#     selected_semester_name = ""

#     if batch_filter:
#         batch = Batch.objects.filter(id=batch_filter).first()
#         selected_batch_name = batch.name if batch else ""
    
#     if section_filter:
#         section = Section.objects.filter(id=section_filter).first()
#         selected_section_name = section.name if section else ""
    
#     if discipline_filter:
#         discipline = Discipline.objects.filter(id=discipline_filter).first()
#         selected_discipline_name = f"{discipline.field} ({discipline.program})" if discipline else ""
    
#     if semester_filter:
#         semester = Semester.objects.filter(id=semester_filter).first()
#         selected_semester_name = f"Semester {semester.number}" if semester else ""

#     return render(request, "fees/fee_list.html", {
#         "student_fees": student_fees.values(),
#         "batches": all_batches,
#         "semesters": semesters,
#         "sections": all_sections,
#         "disciplines": disciplines,
#         "selected_batch": batch_filter,
#         "selected_semester": semester_filter,
#         "selected_section": section_filter,
#         "selected_discipline": discipline_filter,
#         "selected_batch_name": selected_batch_name,
#         "selected_section_name": selected_section_name,
#         "selected_discipline_name": selected_discipline_name,
#         "selected_semester_name": selected_semester_name,
#     })

# def clear_fee(request, fee_id):
#     fee = get_object_or_404(UploadFee, id=fee_id)
    
#     # Check if fee is already cleared
#     if ClearFee.objects.filter(upload_fee=fee).exists():
#         messages.info(request, "Fee already cleared.")
#         return redirect("fee_list")

#     if request.method == "POST":
#         receipt_number = request.POST.get("receipt_number")
#         cleared_amount = request.POST.get("cleared_amount")
#         payment_method = request.POST.get("payment_method")
#         collector_name = request.POST.get("collector_name")
#         remarks = request.POST.get("remarks")

#         ClearFee.objects.create(
#             upload_fee=fee,
#             receipt_number=receipt_number,
#             cleared_amount=cleared_amount,
#             payment_method=payment_method,
#             collector_name=collector_name,
#             remarks=remarks
#         )

#         messages.success(request, "Fee cleared.")
#         return redirect("fee_list")

#     return render(request, "fees/clear_fee.html", {"fee": fee})

# def defaulter_student(request):
#     batches = Batch.objects.all()
#     semesters = Semester.objects.all()
#     sections = Section.objects.all()

#     fees = UploadFee.objects.select_related("student", "batch", "semester", "section")

#     batch_filter = request.GET.get("batch")
#     semester_filter = request.GET.get("semester")
#     section_filter = request.GET.get("section")

#     if batch_filter:
#         fees = fees.filter(batch_id=batch_filter)
#     if semester_filter:
#         fees = fees.filter(semester_id=semester_filter)
#     if section_filter:
#         fees = fees.filter(section_id=section_filter)

#     # Only keep pending fees (fees without ClearFee record)
#     pending_fees = []
#     for fee in fees:
#         # Check if this fee has a ClearFee record
#         is_cleared = ClearFee.objects.filter(upload_fee=fee).exists()
        
#         if not is_cleared:  # Only include defaulters
#             pending_fees.append(fee)

#     return render(request, "fees/defaulter_student.html", {
#         "fees": pending_fees,
#         "batches": batches,
#         "semesters": semesters,
#         "sections": sections,
#         "selected_batch": batch_filter,
#         "selected_semester": semester_filter,
#         "selected_section": section_filter,
#     })


# def student_fee_detail(request, student_id):

#     """
#     View to display detailed fee information for a specific student
#     """
#     student = get_object_or_404(Student, id=student_id)
    
#     # Get all fee records for this student
#     fees = UploadFee.objects.filter(student=student).select_related(
#         'batch', 'section', 'semester', 'discipline'
#     ).prefetch_related('clear_record').order_by('semester_option')
    
#     # Calculate totals from database aggregates
#     totals = fees.aggregate(
#         total_amount=Sum('amount'),
#         total_fine=Sum('fine')
#     )
    
#     total_amount = totals['total_amount'] or 0
#     total_fine = totals['total_fine'] or 0
#     total_fee_due = total_amount + total_fine
    
#     # Calculate total paid from ClearFee records
#     cleared_fees = ClearFee.objects.filter(upload_fee__student=student)
#     total_paid = cleared_fees.aggregate(
#         total_paid=Sum('cleared_amount')
#     )['total_paid'] or 0
    
#     # OR calculate from fees with clear_record
#     # total_paid = sum(fee.clear_record.cleared_amount 
#     #                  for fee in fees if hasattr(fee, 'clear_record'))
    
#     remaining_fee = total_fee_due - total_paid
    
#     # Calculate payment percentage
#     payment_percentage = 0
#     if total_fee_due > 0:
#         payment_percentage = (total_paid / total_fee_due) * 100
    
#     # Prepare fee data for template
#     fee_list = []
#     pending_semesters = []
    
#     for fee in fees:
#         fee_total = fee.amount + fee.fine
        
#         if hasattr(fee, 'clear_record'):
#             clear_record = fee.clear_record
#             paid_amount = clear_record.cleared_amount
#             is_cleared = True
#             balance = fee_total - paid_amount
#             receipt_number = clear_record.receipt_number
#             payment_date = clear_record.cleared_date
#             payment_method = clear_record.payment_method
#         else:
#             paid_amount = 0
#             is_cleared = False
#             balance = fee_total
#             receipt_number = None
#             payment_date = None
#             payment_method = None
        
#         # Check if overdue
#         is_overdue = False
#         if fee.due_date and fee.due_date < timezone.now().date() and not is_cleared:
#             is_overdue = True
        
#         # Add to pending semesters
#         if not is_cleared and balance > 0:
#             pending_semesters.append(fee.semester_option)
        
#         fee_data = {
#             'id': fee.id,
#             'semester_option': fee.semester_option,
#             'amount': fee.amount,
#             'fine': fee.fine,
#             'total_fee': fee_total,
#             'paid_amount': paid_amount,
#             'balance': balance,
#             'is_cleared': is_cleared,
#             'is_overdue': is_overdue,
#             'due_date': fee.due_date,
#             'payment_date': payment_date,
#             'receipt_number': receipt_number,
#             'payment_method': payment_method,
#             'batch': fee.batch,
#             'section': fee.section,
#             'discipline': fee.discipline,
#             'upload_date': fee.upload_date,
#         }
        
#         fee_list.append(fee_data)
    
#     # DEBUG: Print calculations to console
#     print(f"DEBUG - Student: {student.student_id}")
#     print(f"DEBUG - Total Fee Records: {fees.count()}")
#     print(f"DEBUG - Total Amount: {total_amount}")
#     print(f"DEBUG - Total Fine: {total_fine}")
#     print(f"DEBUG - Total Fee Due: {total_fee_due}")
#     print(f"DEBUG - Total Paid: {total_paid}")
#     print(f"DEBUG - Remaining Fee: {remaining_fee}")
#     print(f"DEBUG - Pending Semesters: {pending_semesters}")
    
#     # Show individual fee breakdown
#     for fee in fee_list:
#         print(f"DEBUG - Sem {fee['semester_option']}: Amount={fee['amount']}, Fine={fee['fine']}, Paid={fee['paid_amount']}, Balance={fee['balance']}")
    
#     context = {
#         'student': student,
#         'fees': fee_list,
#         'total_fee_payable': total_fee_due,
#         'total_paid': total_paid,
#         'total_fine': total_fine,
#         'balance_due': remaining_fee,
#         'payment_percentage': round(payment_percentage, 2),
#         'pending_semesters': list(set(pending_semesters)),
#         'current_date': timezone.now().date(),
#     }
    
#     return render(request, 'fees/student_fee_detail.html', context)



# # ----------------


# # @login_required
# # @require_http_methods(["GET", "POST"])
# def edit_fee(request, fee_id):
   
#     # Check permissions
#     if not request.user.has_perm('fees.change_uploadfee'):
#         messages.error(request, "You don't have permission to edit fees.")
#         return redirect('fee_list')
    
#     fee = get_object_or_404(UploadFee, id=fee_id)
    
#     # Check if fee is already cleared
#     if ClearFee.objects.filter(upload_fee=fee).exists():
#         messages.warning(request, "Cannot edit a fee that has already been cleared.")
#         return redirect('fee_list')
    
#     if request.method == "POST":
#         try:
#             # Get form data
#             semester_option = request.POST.get("semester_option")
#             amount_str = request.POST.get("amount")
#             fine_str = request.POST.get("fine")
#             due_date_str = request.POST.get("due_date")
            
#             # Convert and validate amount
#             try:
#                 amount = Decimal(amount_str) if amount_str and amount_str.strip() else Decimal('0')
#             except (InvalidOperation, ValueError, TypeError):
#                 amount = Decimal('0')
            
#             # Convert and validate fine
#             try:
#                 fine = Decimal(fine_str) if fine_str and fine_str.strip() else Decimal('0')
#             except (InvalidOperation, ValueError, TypeError):
#                 fine = Decimal('0')
            
#             # Validate due date
#             if due_date_str:
#                 try:
#                     due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
#                 except:
#                     due_date = fee.due_date
#             else:
#                 due_date = fee.due_date
            
#             # Ensure non-negative values
#             if amount < 0:
#                 amount = Decimal('0')
#             if fine < 0:
#                 fine = Decimal('0')
            
#             # Update the fee record
#             fee.semester_option = semester_option
#             fee.amount = amount
#             fee.fine = fine
#             fee.due_date = due_date
#             fee.save()
            
#             messages.success(request, f"Fee record for {fee.student.name} updated successfully.")
#             return redirect('fee_list')
            
#         except Exception as e:
#             messages.error(request, f"Error updating fee: {str(e)}")
#             return render(request, "fees/edit_fee.html", {
#                 "fee": fee,
#                 "error": str(e)
#             })
    
#     # GET request - show edit form
#     return render(request, "fees/edit_fee.html", {"fee": fee})


# # @login_required
# # @require_http_methods(["POST"])
# def delete_fee(request, fee_id):
#     """
#     View to delete a fee record
#     """
#     # Check permissions
#     if not request.user.has_perm('fees.delete_uploadfee'):
#         messages.error(request, "You don't have permission to delete fees.")
#         return redirect('fee_list')
    
#     fee = get_object_or_404(UploadFee, id=fee_id)
    
#     # Check if fee is already cleared
#     if ClearFee.objects.filter(upload_fee=fee).exists():
#         messages.warning(request, "Cannot delete a fee that has already been cleared.")
#         return redirect('fee_list')
    
#     try:
#         student_name = fee.student.name
#         fee.delete()
#         messages.success(request, f"Fee record for {student_name} deleted successfully.")
#     except Exception as e:
#         messages.error(request, f"Error deleting fee: {str(e)}")
    
#     return redirect('fee_list')


# # @login_required
# # @require_http_methods(["POST"])
# def delete_fee_ajax(request, fee_id):
#     """
#     AJAX endpoint for deleting fee records
#     """
#     if not request.user.has_perm('fees.delete_uploadfee'):
#         return JsonResponse({
#             'success': False,
#             'message': 'You do not have permission to delete fees.'
#         }, status=403)
    
#     fee = get_object_or_404(UploadFee, id=fee_id)
    
#     # Check if fee is already cleared
#     if ClearFee.objects.filter(upload_fee=fee).exists():
#         return JsonResponse({
#             'success': False,
#             'message': 'Cannot delete a fee that has already been cleared.'
#         })
    
#     try:
#         student_name = fee.student.name
#         fee_id = fee.id
#         fee.delete()
        
#         return JsonResponse({
#             'success': True,
#             'message': f'Fee record deleted successfully.',
#             'fee_id': fee_id,
#             'student_name': student_name
#         })
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'message': f'Error deleting fee: {str(e)}'
#         }, status=500)


# # @login_required
# # @require_http_methods(["POST"])
# def bulk_delete_fees(request):
#     """
#     View to delete multiple fee records at once
#     """
#     if not request.user.has_perm('fees.delete_uploadfee'):
#         messages.error(request, "You don't have permission to delete fees.")
#         return redirect('fee_list')
    
#     fee_ids = request.POST.getlist('fee_ids[]')
    
#     if not fee_ids:
#         messages.warning(request, "No fees selected for deletion.")
#         return redirect('fee_list')
    
#     deleted_count = 0
#     error_count = 0
    
#     with transaction.atomic():
#         for fee_id in fee_ids:
#             try:
#                 fee = UploadFee.objects.get(id=fee_id)
                
#                 # Skip if fee is cleared
#                 if ClearFee.objects.filter(upload_fee=fee).exists():
#                     error_count += 1
#                     continue
                
#                 fee.delete()
#                 deleted_count += 1
#             except UploadFee.DoesNotExist:
#                 error_count += 1
#             except Exception:
#                 error_count += 1
    
#     if deleted_count > 0:
#         messages.success(request, f"Successfully deleted {deleted_count} fee record(s).")
    
#     if error_count > 0:
#         messages.warning(request, f"Could not delete {error_count} fee record(s) (may be cleared or not found).")
    
#     return redirect('fee_list')

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import ClearFee, UploadFee
from student.models import Student, Batch, Semester, Section, Discipline
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from django.db.models import Sum
import json



# Helper function to check permissions
def can_edit_fee(user):
    """Check if user has permission to edit fees"""
    # Superusers and staff can always edit
    if user.is_superuser or user.is_staff:
        return True
    
    # Check for specific permission
    if user.has_perm('fees.change_uploadfee'):
        return True
    
    # Check for group membership (if using groups)
    if user.groups.filter(name__in=['Fee Managers', 'Accountants', 'Administrators']).exists():
        return True
    
    return False


def can_delete_fee(user):
    """Check if user has permission to delete fees"""
    # Superusers and staff can always delete
    if user.is_superuser or user.is_staff:
        return True
    
    # Check for specific permission
    if user.has_perm('fees.delete_uploadfee'):
        return True
    
    # Check for group membership
    if user.groups.filter(name__in=['Fee Managers', 'Administrators']).exists():
        return True
    
    return False


def upload_fee(request):
    batches = Batch.objects.all()
    semesters = Semester.objects.all()
    sections = Section.objects.all()
    disciplines = Discipline.objects.all()

    students = None

    if request.method == "POST":
        discipline_id = request.POST.get("discipline")
        batch_id = request.POST.get("batch")
        section_id = request.POST.get("section")
        semester_id = request.POST.get("semester")
        semester_option = request.POST.get("semester_option")

        amount_default = request.POST.get("amount")
        due_date_str = request.POST.get("due_date")
        fine_amount = request.POST.get("fine_amount", "5000")

        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except:
                due_date = date.today()
        else:
            due_date = date.today()

        if "load_students" in request.POST:
            students = Student.objects.filter(
                batch_id=batch_id,
                semester_id=semester_id,
                section_id=section_id,
                discipline_id=discipline_id
            )

        if "submit_all" in request.POST:
            students = Student.objects.filter(
                batch_id=batch_id,
                semester_id=semester_id,
                section_id=section_id,
                discipline_id=discipline_id
            )

            today = date.today()
            
            try:
                auto_fine = Decimal(fine_amount) if fine_amount else Decimal('5000')
            except (InvalidOperation, ValueError, TypeError):
                auto_fine = Decimal('5000')

            with transaction.atomic():
                for st in students:
                    base_amount_str = request.POST.get(f"base_amount_{st.id}", amount_default)
                    fine_amount_str = request.POST.get(f"fine_amount_{st.id}", fine_amount)
                    
                    try:
                        amount = Decimal(base_amount_str) if base_amount_str and base_amount_str.strip() else Decimal('0')
                    except (InvalidOperation, ValueError, TypeError):
                        amount = Decimal('0')
                        
                    try:
                        student_fine = Decimal(fine_amount_str) if fine_amount_str and fine_amount_str.strip() else auto_fine
                    except (InvalidOperation, ValueError, TypeError):
                        student_fine = auto_fine
                    
                    if amount is None or amount < 0:
                        amount = Decimal('0')
                    
                    final_fine = student_fine
                    if today > due_date:
                        final_fine += Decimal('100')

                    UploadFee.objects.update_or_create(
                        student=st,
                        semester_option=semester_option,
                        defaults={
                            "batch_id": batch_id,
                            "semester_id": semester_id,
                            "section_id": section_id,
                            "discipline_id": discipline_id,
                            "amount": amount,
                            "fine": final_fine,
                            "due_date": due_date
                        }
                    )

            messages.success(request, "Fees uploaded successfully.")
            return redirect("fee_list")

    return render(
        request,
        "fees/upload_fee.html",
        {
            "batches": batches,
            "semesters": semesters,
            "sections": sections,
            "disciplines": disciplines,
            "students": students,
        }
    )


def fee_list(request):
    batches = Batch.objects.all()
    semesters = Semester.objects.all()
    disciplines = Discipline.objects.all()

    batch_filter = request.GET.get("batch")
    semester_filter = request.GET.get("semester")
    section_filter = request.GET.get("section")
    discipline_filter = request.GET.get("discipline")

    all_sections = Section.objects.select_related('batch').all()
    all_batches = Batch.objects.select_related('discipline').all()

    fees = UploadFee.objects.select_related(
        "student", "batch", "semester", "section", "discipline"
    )

    if batch_filter:
        fees = fees.filter(batch_id=batch_filter)
    if semester_filter:
        fees = fees.filter(semester_id=semester_filter)
    if section_filter:
        fees = fees.filter(section_id=section_filter)
    if discipline_filter:
        fees = fees.filter(discipline_id=discipline_filter)

    student_fees = {}
    for fee in fees:
        student_id = fee.student.id
        if student_id not in student_fees:
            student_fees[student_id] = {
                'student': fee.student,
                'batch': fee.batch,
                'semester': fee.semester,
                'section': fee.section,
                'fees': [],
                'total_all': 0,
                'total_pending': 0,
                'total_cleared': 0,
            }
        
        fee.is_cleared = ClearFee.objects.filter(upload_fee=fee).exists()
        student_fees[student_id]['fees'].append(fee)
        
        student_fees[student_id]['total_all'] += fee.total_fee()
        
        if fee.is_cleared:
            student_fees[student_id]['total_cleared'] += fee.total_fee()
        else:
            student_fees[student_id]['total_pending'] += fee.total_fee()

    selected_batch_name = ""
    selected_section_name = ""
    selected_discipline_name = ""
    selected_semester_name = ""

    if batch_filter:
        batch = Batch.objects.filter(id=batch_filter).first()
        selected_batch_name = batch.name if batch else ""
    
    if section_filter:
        section = Section.objects.filter(id=section_filter).first()
        selected_section_name = section.name if section else ""
    
    if discipline_filter:
        discipline = Discipline.objects.filter(id=discipline_filter).first()
        selected_discipline_name = f"{discipline.field} ({discipline.program})" if discipline else ""
    
    if semester_filter:
        semester = Semester.objects.filter(id=semester_filter).first()
        selected_semester_name = f"Semester {semester.number}" if semester else ""

    # Check user permissions
    user_can_edit = can_edit_fee(request.user) if request.user.is_authenticated else False
    user_can_delete = can_delete_fee(request.user) if request.user.is_authenticated else False

    return render(request, "fees/fee_list.html", {
        "student_fees": student_fees.values(),
        "batches": all_batches,
        "semesters": semesters,
        "sections": all_sections,
        "disciplines": disciplines,
        "selected_batch": batch_filter,
        "selected_semester": semester_filter,
        "selected_section": section_filter,
        "selected_discipline": discipline_filter,
        "selected_batch_name": selected_batch_name,
        "selected_section_name": selected_section_name,
        "selected_discipline_name": selected_discipline_name,
        "selected_semester_name": selected_semester_name,
        "user_can_edit": user_can_edit,
        "user_can_delete": user_can_delete,
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

def clear_fee(request, fee_id):
    fee = get_object_or_404(UploadFee, id=fee_id)
    
    # Calculate total fee manually
    total_fee_value = Decimal('0')
    
    if hasattr(fee, 'amount'):
        total_fee_value = fee.amount
    
    # Add fine amount if exists
    if hasattr(fee, 'fine_amount'):
        total_fee_value += fee.fine_amount
    
    # Calculate total already paid
    total_paid = ClearFee.objects.filter(upload_fee=fee).aggregate(
        total=Sum('cleared_amount')
    )['total'] or Decimal('0')
    
    # Calculate remaining amount
    remaining_amount = total_fee_value - total_paid
    
    # If fee is already fully paid
    if remaining_amount <= 0:
        messages.info(request, f"Fee is already fully paid. Total paid: PKR {total_paid:.2f}")
        # Redirect to fee list instead
        return redirect("fee_list")

    if request.method == "POST":
        receipt_number = request.POST.get("receipt_number")
        cleared_amount = Decimal(request.POST.get("cleared_amount", 0))
        payment_method = request.POST.get("payment_method")
        collector_name = request.POST.get("collector_name")
        remarks = request.POST.get("remarks")
        
        # Validate
        if cleared_amount <= Decimal('0'):
            messages.error(request, "Payment amount must be greater than 0.")
        elif cleared_amount > remaining_amount:
            messages.error(request, f"Payment amount cannot exceed remaining amount: PKR {remaining_amount:.2f}")
        else:
            # Create payment record
            ClearFee.objects.create(
                upload_fee=fee,
                receipt_number=receipt_number,
                cleared_amount=cleared_amount,
                payment_method=payment_method,
                collector_name=collector_name,
                remarks=remarks
            )
            
            # Calculate new totals
            new_total_paid = total_paid + cleared_amount
            new_remaining = remaining_amount - cleared_amount
            
            # Update fee status
            if new_total_paid >= total_fee_value:
                fee.status = 'paid'
                messages.success(request, f"✅ Fee fully cleared! Total paid: PKR {new_total_paid:.2f}")
            else:
                fee.status = 'partial'
                messages.success(request, f"✅ Partial payment of PKR {cleared_amount:.2f} received. Remaining: PKR {new_remaining:.2f}")
            
            fee.save()
            
            # FIX: Redirect to fee_list instead of student_fees
            return redirect("fee_list")
    
    # Get payment history
    payment_history = ClearFee.objects.filter(upload_fee=fee).order_by('-id')
    
    return render(request, "fees/clear_fee.html", {
        "fee": fee,
        "total_fee": total_fee_value,
        "total_paid": total_paid,
        "remaining_amount": remaining_amount,
        "payment_history": payment_history
    })
def defaulter_student(request):
    batches = Batch.objects.all()
    semesters = Semester.objects.all()
    sections = Section.objects.all()

    fees = UploadFee.objects.select_related("student", "batch", "semester", "section")

    batch_filter = request.GET.get("batch")
    semester_filter = request.GET.get("semester")
    section_filter = request.GET.get("section")

    if batch_filter:
        fees = fees.filter(batch_id=batch_filter)
    if semester_filter:
        fees = fees.filter(semester_id=semester_filter)
    if section_filter:
        fees = fees.filter(section_id=section_filter)

    pending_fees = []
    for fee in fees:
        is_cleared = ClearFee.objects.filter(upload_fee=fee).exists()
        
        if not is_cleared:
            pending_fees.append(fee)

    return render(request, "fees/defaulter_student.html", {
        "fees": pending_fees,
        "batches": batches,
        "semesters": semesters,
        "sections": sections,
        "selected_batch": batch_filter,
        "selected_semester": semester_filter,
        "selected_section": section_filter,
    })


def student_fee_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    fees = UploadFee.objects.filter(student=student).select_related(
        'batch', 'section', 'semester', 'discipline'
    ).prefetch_related('clear_record').order_by('semester_option')
    
    totals = fees.aggregate(
        total_amount=Sum('amount'),
        total_fine=Sum('fine')
    )
    
    total_amount = totals['total_amount'] or 0
    total_fine = totals['total_fine'] or 0
    total_fee_due = total_amount + total_fine
    
    cleared_fees = ClearFee.objects.filter(upload_fee__student=student)
    total_paid = cleared_fees.aggregate(
        total_paid=Sum('cleared_amount')
    )['total_paid'] or 0
    
    remaining_fee = total_fee_due - total_paid
    
    payment_percentage = 0
    if total_fee_due > 0:
        payment_percentage = (total_paid / total_fee_due) * 100
    
    fee_list = []
    pending_semesters = []
    
    for fee in fees:
        fee_total = fee.amount + fee.fine
        
        if hasattr(fee, 'clear_record'):
            clear_record = fee.clear_record
            paid_amount = clear_record.cleared_amount
            is_cleared = True
            balance = fee_total - paid_amount
            receipt_number = clear_record.receipt_number
            payment_date = clear_record.cleared_date
            payment_method = clear_record.payment_method
        else:
            paid_amount = 0
            is_cleared = False
            balance = fee_total
            receipt_number = None
            payment_date = None
            payment_method = None
        
        is_overdue = False
        if fee.due_date and fee.due_date < timezone.now().date() and not is_cleared:
            is_overdue = True
        
        if not is_cleared and balance > 0:
            pending_semesters.append(fee.semester_option)
        
        fee_data = {
            'id': fee.id,
            'semester_option': fee.semester_option,
            'amount': fee.amount,
            'fine': fee.fine,
            'total_fee': fee_total,
            'paid_amount': paid_amount,
            'balance': balance,
            'is_cleared': is_cleared,
            'is_overdue': is_overdue,
            'due_date': fee.due_date,
            'payment_date': payment_date,
            'receipt_number': receipt_number,
            'payment_method': payment_method,
            'batch': fee.batch,
            'section': fee.section,
            'discipline': fee.discipline,
            'upload_date': fee.upload_date,
        }
        
        fee_list.append(fee_data)
    
    context = {
        'student': student,
        'fees': fee_list,
        'total_fee_payable': total_fee_due,
        'total_paid': total_paid,
        'total_fine': total_fine,
        'balance_due': remaining_fee,
        'payment_percentage': round(payment_percentage, 2),
        'pending_semesters': list(set(pending_semesters)),
        'current_date': timezone.now().date(),
    }
    
    return render(request, 'fees/student_fee_detail.html', context)


def edit_fee(request, fee_id):
    """View to edit an existing fee record"""
    
    # Check permissions
    if not request.user.is_authenticated:
        messages.error(request, "Please login to edit fees.")
        return redirect('login')
    
    if not can_edit_fee(request.user):
        messages.error(request, "You don't have permission to edit fees.")
        return redirect('fee_list')
    
    fee = get_object_or_404(UploadFee, id=fee_id)
    
    # Check if fee is already cleared
    if ClearFee.objects.filter(upload_fee=fee).exists():
        messages.warning(request, "Cannot edit a fee that has already been cleared.")
        return redirect('fee_list')
    
    if request.method == "POST":
        try:
            # Get form data
            semester_option = request.POST.get("semester_option")
            amount_str = request.POST.get("amount")
            fine_str = request.POST.get("fine")
            due_date_str = request.POST.get("due_date")
            
            # Convert and validate amount
            try:
                amount = Decimal(amount_str) if amount_str and amount_str.strip() else Decimal('0')
            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, "Invalid amount format. Please enter a valid number.")
                return render(request, "fees/edit_fee.html", {"fee": fee})
            
            # Convert and validate fine
            try:
                fine = Decimal(fine_str) if fine_str and fine_str.strip() else Decimal('0')
            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, "Invalid fine format. Please enter a valid number.")
                return render(request, "fees/edit_fee.html", {"fee": fee})
            
            # Validate due date
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                except:
                    due_date = fee.due_date
                    messages.warning(request, "Invalid date format. Using existing due date.")
            else:
                due_date = fee.due_date
            
            # Ensure non-negative values
            if amount < 0:
                amount = Decimal('0')
                messages.warning(request, "Amount cannot be negative. Set to 0.")
            if fine < 0:
                fine = Decimal('0')
                messages.warning(request, "Fine cannot be negative. Set to 0.")
            
            # Check if amount is too large
            if amount > Decimal('1000000'):
                messages.error(request, "Amount is too large. Maximum is 1,000,000.")
                return render(request, "fees/edit_fee.html", {"fee": fee})
            
            # Update the fee record
            fee.semester_option = semester_option
            fee.amount = amount
            fee.fine = fine
            fee.due_date = due_date
            fee.save()
            
            messages.success(request, f"Fee record for {fee.student.name} updated successfully.")
            return redirect('fee_list')
            
        except Exception as e:
            messages.error(request, f"Error updating fee: {str(e)}")
            return render(request, "fees/edit_fee.html", {
                "fee": fee,
                "error": str(e)
            })
    
    # GET request - show edit form
    return render(request, "fees/edit_fee.html", {
        "fee": fee,
        "user_can_delete": can_delete_fee(request.user),
    })


def delete_fee(request, fee_id):
    """View to delete a fee record"""
    
    if not request.user.is_authenticated:
        messages.error(request, "Please login to delete fees.")
        return redirect('login')
    
    if not can_delete_fee(request.user):
        messages.error(request, "You don't have permission to delete fees.")
        return redirect('fee_list')
    
    fee = get_object_or_404(UploadFee, id=fee_id)
    
    # Check if fee is already cleared
    if ClearFee.objects.filter(upload_fee=fee).exists():
        messages.warning(request, "Cannot delete a fee that has already been cleared.")
        return redirect('fee_list')
    
    try:
        student_name = fee.student.name
        fee.delete()
        messages.success(request, f"Fee record for {student_name} deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting fee: {str(e)}")
    
    return redirect('fee_list')


def delete_fee_ajax(request, fee_id):
    """AJAX endpoint for deleting fee records"""
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please login to delete fees.',
            'redirect': '/login/'
        }, status=401)
    
    if not can_delete_fee(request.user):
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to delete fees.',
            'redirect': '/fees/list/'
        }, status=403)
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'
        }, status=400)
    
    fee = get_object_or_404(UploadFee, id=fee_id)
    
    # Check if fee is already cleared
    if ClearFee.objects.filter(upload_fee=fee).exists():
        return JsonResponse({
            'success': False,
            'message': 'Cannot delete a fee that has already been cleared.'
        })
    
    try:
        student_name = fee.student.name
        fee_amount = fee.amount
        fee.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Fee record for {student_name} (Rs. {fee_amount}) deleted successfully.',
            'fee_id': fee_id,
            'student_name': student_name
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting fee: {str(e)}'
        }, status=500)


def bulk_delete_fees(request):
    """View to delete multiple fee records at once"""
    
    if not request.user.is_authenticated:
        messages.error(request, "Please login to delete fees.")
        return redirect('login')
    
    if not can_delete_fee(request.user):
        messages.error(request, "You don't have permission to delete fees.")
        return redirect('fee_list')
    
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('fee_list')
    
    fee_ids = request.POST.getlist('fee_ids[]')
    
    if not fee_ids:
        messages.warning(request, "No fees selected for deletion.")
        return redirect('fee_list')
    
    deleted_count = 0
    error_count = 0
    cleared_count = 0
    
    with transaction.atomic():
        for fee_id in fee_ids:
            try:
                fee = UploadFee.objects.get(id=fee_id)
                
                # Skip if fee is cleared
                if ClearFee.objects.filter(upload_fee=fee).exists():
                    cleared_count += 1
                    continue
                
                fee.delete()
                deleted_count += 1
            except UploadFee.DoesNotExist:
                error_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error deleting fee {fee_id}: {e}")
    
    if deleted_count > 0:
        messages.success(request, f"Successfully deleted {deleted_count} fee record(s).")
    
    if cleared_count > 0:
        messages.warning(request, f"Skipped {cleared_count} fee record(s) that were already cleared.")
    
    if error_count > 0:
        messages.error(request, f"Could not delete {error_count} fee record(s).")
    
    return redirect('fee_list')


def toggle_fee_status(request, fee_id):
    """Toggle fee clearance status"""
    
    if not request.user.is_authenticated:
        messages.error(request, "Please login to modify fees.")
        return redirect('login')
    
    if not can_edit_fee(request.user):
        messages.error(request, "You don't have permission to modify fees.")
        return redirect('fee_list')
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    
    fee = get_object_or_404(UploadFee, id=fee_id)
    
    try:
        is_cleared = ClearFee.objects.filter(upload_fee=fee).exists()
        
        if is_cleared:
            # Clear the clearance record
            ClearFee.objects.filter(upload_fee=fee).delete()
            status = "pending"
            message = f"Fee for {fee.student.name} marked as pending."
        else:
            # Create clearance record
            ClearFee.objects.create(
                upload_fee=fee,
                receipt_number=f"AUTO-{fee.id}",
                cleared_amount=fee.amount,
                payment_method="Manual",
                collector_name=request.user.get_full_name() or request.user.username,
                remarks="Status toggled manually"
            )
            status = "cleared"
            message = f"Fee for {fee.student.name} marked as cleared."
        
        return JsonResponse({
            'success': True,
            'message': message,
            'status': status,
            'fee_id': fee_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error toggling fee status: {str(e)}'
        }, status=500)


# Helper view to check permissions (for debugging)
def check_permissions(request):
    """Debug view to check user permissions"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'})
    
    permissions = {
        'username': request.user.username,
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'groups': list(request.user.groups.values_list('name', flat=True)),
        'all_permissions': list(request.user.get_all_permissions()),
        'can_edit_fee': can_edit_fee(request.user),
        'can_delete_fee': can_delete_fee(request.user),
        'has_fees.change_uploadfee': request.user.has_perm('fees.change_uploadfee'),
        'has_fees.delete_uploadfee': request.user.has_perm('fees.delete_uploadfee'),
    }
    
    return JsonResponse(permissions)


# Add this to automatically create permissions for testing
def setup_permissions(request):
    """Create test users and permissions (for development only)"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Superuser required'})
    
    from django.contrib.auth.models import User, Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from .models import UploadFee
    
    # Create groups
    fee_manager_group, created = Group.objects.get_or_create(name='Fee Managers')
    accountant_group, created = Group.objects.get_or_create(name='Accountants')
    
    # Get permissions
    content_type = ContentType.objects.get_for_model(UploadFee)
    
    change_permission = Permission.objects.get(
        codename='change_uploadfee',
        content_type=content_type
    )
    delete_permission = Permission.objects.get(
        codename='delete_uploadfee',
        content_type=content_type
    )
    
    # Add permissions to groups
    fee_manager_group.permissions.add(change_permission, delete_permission)
    accountant_group.permissions.add(change_permission)
    
    # Create test users
    test_users = [
        {'username': 'fee_manager', 'password': 'test123', 'groups': ['Fee Managers']},
        {'username': 'accountant', 'password': 'test123', 'groups': ['Accountants']},
        {'username': 'regular', 'password': 'test123', 'groups': []},
    ]
    
    for user_data in test_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={'is_staff': True}
        )
        user.set_password(user_data['password'])
        user.save()
        
        for group_name in user_data['groups']:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
    
    return JsonResponse({
        'message': 'Permissions setup complete',
        'test_users': test_users
    })