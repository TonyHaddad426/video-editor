/** @type {import('next').NextConfig} */
const videoBucketHostname = process.env.NEXT_PUBLIC_S3_VIDEO_BUCKET_HOSTNAME;

const nextConfig = {
    images: {
      remotePatterns: [
        {
          protocol: 'https',
          hostname: videoBucketHostname,
          port: '',
          pathname: '/*',
        },
      ],
    },
  }

module.exports = nextConfig

