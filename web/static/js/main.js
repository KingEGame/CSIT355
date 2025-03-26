// Common functionality for all pages
$(document).ready(function() {
    // Add fade-in animation to cards and tables
    $('.card, .table').addClass('fade-in');

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle form submissions with loading state
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        if (submitBtn.length) {
            submitBtn.prop('disabled', true);
            submitBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...');
        }
    });

    // Handle AJAX errors globally
    $(document).ajaxError(function(event, jqXHR, settings, error) {
        console.error('AJAX Error:', error);
        alert('An error occurred. Please try again later.');
    });

    // Add loading state to buttons during AJAX requests
    $(document).ajaxStart(function() {
        $('.btn').prop('disabled', true);
    }).ajaxStop(function() {
        $('.btn').prop('disabled', false);
    });

    // Handle modal form submissions
    $('.modal form').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const submitBtn = form.find('button[type="submit"]');
        const modal = form.closest('.modal');

        submitBtn.prop('disabled', true);
        submitBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...');

        $.ajax({
            url: form.attr('action'),
            method: form.attr('method'),
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    modal.modal('hide');
                    location.reload();
                } else {
                    alert(response.message || 'An error occurred.');
                }
            },
            error: function() {
                alert('An error occurred. Please try again.');
            },
            complete: function() {
                submitBtn.prop('disabled', false);
                submitBtn.html('Submit');
            }
        });
    });

    // Handle search input with debounce
    let searchTimeout;
    $('input[type="search"]').on('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function() {
            $(this).closest('form').submit();
        }.bind(this), 500);
    });

    // Add confirmation for destructive actions
    $('.btn-danger').on('click', function(e) {
        if (!confirm('Are you sure you want to proceed with this action?')) {
            e.preventDefault();
        }
    });

    // Handle responsive table scrolling
    $('.table-responsive').on('scroll', function() {
        $(this).addClass('scrolling');
    }).on('scrollend', function() {
        $(this).removeClass('scrolling');
    });
}); 