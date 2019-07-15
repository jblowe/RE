% if 'errors' in data:
    <div class="alert alert-danger" role="alert">
        % for e in data['errors']:
            <p>{{ e }}</p>
        % end
    </div>
% end
