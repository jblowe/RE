% if 'errors' in data:
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
        % for e in data['errors']:
            <p>{{ e }}</p>
        % end
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    </div>
% end
% if 'messages' in data:
    <div class="alert alert-success alert-dismissible fade show" role="alert">
        % for m in data['messages']:
            <p>{{ m }}</p>
        % end
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    </div>
% end