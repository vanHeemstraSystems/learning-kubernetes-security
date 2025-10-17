FROM nginx:1.25-alpine

# Create non-root user

RUN addgroup -g 1001 -S nginx-custom && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx-custom -g nginx-custom nginx-custom

# Copy custom nginx configuration

COPY nginx.conf /etc/nginx/nginx.conf

# Copy application files

COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/

# Set proper permissions

RUN chown -R nginx-custom:nginx-custom /usr/share/nginx/html && \
    chown -R nginx-custom:nginx-custom /var/cache/nginx && \
    chown -R nginx-custom:nginx-custom /var/log/nginx && \
    chown -R nginx-custom:nginx-custom /etc/nginx/conf.d

RUN touch /var/run/nginx.pid && \
    chown -R nginx-custom:nginx-custom /var/run/nginx.pid

# Switch to non-root user

USER nginx-custom

# Expose port

EXPOSE 8080

# Health check

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
