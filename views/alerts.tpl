% if 'errors' in data:
    <div class="alert alert-danger" role="alert">
        % for e in data['errors']:
            <p>{{ e }}</p>
        % end
    </div>
% end
% if 'messages' in data:
    <div class="alert alert-success" role="alert">
        % for m in data['messages']:
            <p>{{ m }}</p>
        % end
    </div>
% end
