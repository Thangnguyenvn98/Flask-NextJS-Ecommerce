/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        domains: ['res.cloudinary.com']
      },
    rewrites: async () => {
        return [
            {
                source: '/api/auth/:path*',
                destination: 
                process.env.NODE_ENV === 'development' ?
                '/api/auth/:path*':
                '/api/auth/'
            },

            {
                source: '/api/:path*',
          destination:
          process.env.NODE_ENV === 'development'
            ? 'http://127.0.0.1:8080/api/:path*'
            : '/api/',
            }
        ]
    }
}

module.exports = nextConfig
